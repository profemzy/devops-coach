# =============================================================================
# WackOps-Coach Infrastructure - Main Terraform Configuration
# =============================================================================

terraform {
  required_version = ">= 1.10.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.59"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.7"
    }
  }

  backend "azurerm" {}
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = false
      recover_soft_deleted_key_vaults = true
    }
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

# =============================================================================
# Local Values
# =============================================================================
locals {
  project_name    = "wackopscoach"
  environment     = var.environment
  location        = var.location
  resource_prefix = "${local.project_name}-${local.environment}"

  common_tags = {
    Project     = "WackOps-Coach"
    Environment = local.environment
    ManagedBy   = "Terraform"
    Owner       = "InfoTitans"
    CostCenter  = "DevOps"
  }
}

# =============================================================================
# Resource Group
# =============================================================================
resource "azurerm_resource_group" "main" {
  name     = "${local.resource_prefix}-rg"
  location = local.location
  tags     = local.common_tags
}

# =============================================================================
# Virtual Network and Subnets
# =============================================================================
resource "azurerm_virtual_network" "main" {
  name                = "${local.resource_prefix}-vnet"
  resource_group_name = azurerm_resource_group.main.name
  location            = local.location
  address_space       = var.vnet_address_space
  tags                = local.common_tags
}

resource "azurerm_subnet" "aks" {
  name                 = "aks-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.subnet_aks_prefix]
}

resource "azurerm_network_security_group" "aks" {
  name                = "${local.resource_prefix}-aks-nsg"
  location            = local.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "AllowHTTP"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "Internet"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowHTTPS"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "Internet"
    destination_address_prefix = "*"
  }

  tags = local.common_tags
}

resource "azurerm_subnet_network_security_group_association" "aks" {
  subnet_id                 = azurerm_subnet.aks.id
  network_security_group_id = azurerm_network_security_group.aks.id
}

# =============================================================================
# Azure Container Registry (ACR) - Azure Verified Module v0.5.1
# =============================================================================
module "acr" {
  source  = "Azure/avm-res-containerregistry-registry/azurerm"
  version = "0.5.1"

  name                = "${local.project_name}${var.environment}acr"
  resource_group_name = azurerm_resource_group.main.name
  location            = local.location

  sku             = var.acr_sku
  admin_enabled   = false
  zone_redundancy_enabled = var.acr_sku == "Premium"

  enable_trust_policy = var.acr_sku == "Premium"
  retention_policy_in_days = var.acr_sku == "Premium" ? 30 : 7

  public_network_access_enabled = true

  tags = local.common_tags
}

# =============================================================================
# Azure Kubernetes Service (AKS) - Azure Verified Module v11.0.0
# =============================================================================
module "aks" {
  source  = "Azure/aks/azurerm"
  version = "11.0.0"

  resource_group_name = azurerm_resource_group.main.name
  location            = local.location

  prefix = local.project_name
  cluster_name = "${local.resource_prefix}-aks"

  kubernetes_version        = var.kubernetes_version
  automatic_channel_upgrade = null
  sku_tier                  = var.environment == "prod" ? "Standard" : "Free"

  # System node pool
  agents_pool_name = "system"
  agents_count     = var.aks_node_count
  agents_size      = var.aks_node_vm_size
  agents_min_count = var.aks_min_node_count
  agents_max_count = var.aks_max_node_count
  auto_scaling_enabled = var.aks_enable_auto_scaling

  # Networking
  vnet_subnet = {
    id = azurerm_subnet.aks.id
  }

  network_plugin = "azure"
  network_policy = "calico"

  # OIDC and Workload Identity
  oidc_issuer_enabled       = true
  workload_identity_enabled = true

  # RBAC
  role_based_access_control_enabled = true
  rbac_aad_azure_rbac_enabled       = true
  rbac_aad_admin_group_object_ids   = var.aks_admin_group_ids

  # ACR attachment
  attached_acr_id_map = {
    main = module.acr.resource_id
  }

  # Monitoring
  log_analytics_workspace_enabled = var.log_analytics_workspace_id != null
  log_analytics_workspace = var.log_analytics_workspace_id != null ? {
    id                  = var.log_analytics_workspace_id
    name                = "${local.resource_prefix}-law"
    location            = local.location
    resource_group_name = azurerm_resource_group.main.name
  } : null

  # Maintenance window for production
  maintenance_window = var.environment == "prod" ? {
    allowed = [{
      day   = "Saturday"
      hours = [22, 23, 0, 1, 2]
    }]
    not_allowed = []
  } : null

  tags = local.common_tags

  depends_on = [azurerm_subnet_network_security_group_association.aks]
}

# =============================================================================
# Azure Key Vault - Azure Verified Module v0.10.2
# =============================================================================
module "keyvault" {
  source  = "Azure/avm-res-keyvault-vault/azurerm"
  version = "0.10.2"

  name                = "${local.project_name}-${local.environment}-kv"
  resource_group_name = azurerm_resource_group.main.name
  location            = local.location

  tenant_id = data.azurerm_client_config.current.tenant_id

  sku_name = var.keyvault_sku

  soft_delete_retention_days = 7
  purge_protection_enabled   = var.environment == "prod"

  public_network_access_enabled = true

  tags = local.common_tags
}

data "azurerm_client_config" "current" {}

# Grant AKS managed identity access to Key Vault
resource "azurerm_role_assignment" "aks_keyvault_reader" {
  scope                = module.keyvault.resource_id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = module.aks.cluster_identity.object_id
}

# Grant current user admin access to Key Vault
resource "azurerm_role_assignment" "current_user_keyvault_admin" {
  scope                = module.keyvault.resource_id
  role_definition_name = "Key Vault Administrator"
  principal_id         = data.azurerm_client_config.current.object_id
}

# =============================================================================
# Azure DNS
# =============================================================================
data "azurerm_dns_zone" "existing" {
  name                = var.dns_zone_name
  resource_group_name = var.dns_resource_group_name
}

# =============================================================================
# Outputs
# =============================================================================
output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "vnet_id" {
  description = "ID of the Virtual Network"
  value       = azurerm_virtual_network.main.id
}

output "aks_subnet_id" {
  description = "ID of the AKS subnet"
  value       = azurerm_subnet.aks.id
}

output "acr_login_server" {
  description = "Login server for ACR"
  value       = module.acr.resource.login_server
}

output "acr_name" {
  description = "Name of the ACR"
  value       = module.acr.name
}

output "aks_cluster_name" {
  description = "Name of the AKS cluster"
  value       = module.aks.aks_name
}

output "aks_cluster_fqdn" {
  description = "FQDN of the AKS cluster"
  value       = module.aks.cluster_fqdn
}

output "keyvault_name" {
  description = "Name of the Key Vault"
  value       = module.keyvault.name
}

output "keyvault_uri" {
  description = "URI of the Key Vault"
  value       = module.keyvault.uri
}

output "kube_config_raw" {
  description = "Raw Kubernetes config"
  value       = module.aks.kube_config_raw
  sensitive   = true
}
