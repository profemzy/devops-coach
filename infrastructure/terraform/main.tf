# =============================================================================
# WackOps-Coach Infrastructure - Main Terraform Configuration
# =============================================================================
# This file contains all infrastructure components for the WackOps-Coach
# application running on Azure Kubernetes Service (AKS)
# Using Azure Verified Modules (AVM) for all resources
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
  project_name    = "wackops-coach"
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
# Virtual Network and Subnets (Inlined from custom module)
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

  delegation {
    name = "aks-delegation"
    service_delegation {
      name    = "Microsoft.ContainerService/managedClusters"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
    }
  }
}

resource "azurerm_subnet" "aci" {
  name                 = "aci-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.subnet_aci_prefix]

  delegation {
    name = "aci-delegation"
    service_delegation {
      name    = "Microsoft.ContainerInstance/containerGroups"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
    }
  }
}

resource "azurerm_network_security_group" "aks" {
  name                = "${local.resource_prefix}-aks-nsg"
  location            = local.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "AllowAzureLoadBalancer"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "AzureLoadBalancer"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowHTTP"
    priority                   = 110
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
    priority                   = 120
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
# Azure Container Registry (ACR) - Azure Verified Module v0.1.0
# =============================================================================
module "acr" {
  source  = "Azure/avm-res-containerregistry-registry/azurerm"
  version = "0.1.0"

  name                = "${local.project_name}${local.environment}acr"
  resource_group_name = azurerm_resource_group.main.name
  location            = local.location

  sku             = var.acr_sku
  admin_enabled   = false
  zone_redundancy_enabled = var.acr_sku == "Premium" ? true : false

  trust_policy_enabled = var.acr_sku == "Premium"

  retention_policy = {
    days    = var.acr_sku == "Premium" ? 30 : 7
    enabled = true
  }

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

  cluster_name        = "${local.resource_prefix}-aks"
  prefix              = local.project_name

  kubernetes_version   = var.kubernetes_version
  orchestrator_version = var.kubernetes_version
  sku_tier             = var.environment == "prod" ? "Standard" : "Free"

  # System node pool
  agents_pool_name    = "system"
  agents_count        = var.aks_node_count
  agents_size         = var.aks_node_vm_size
  agents_min_count    = var.aks_min_node_count
  agents_max_count    = var.aks_max_node_count
  enable_auto_scaling = var.aks_enable_auto_scaling

  vnet_subnet_id = azurerm_subnet.aks.id

  network_plugin  = "azure"
  network_policy  = "calico"
  load_balancer_sku = "standard"

  oidc_issuer_enabled       = true
  workload_identity_enabled = true

  rbac_aad_managed = true
  rbac_aad_admin_group_object_ids = var.aks_admin_group_ids

  attached_acr_id_map = {
    main = module.acr.resource_id
  }

  log_analytics_workspace_enabled = var.log_analytics_workspace_id != null
  log_analytics_workspace_id      = var.log_analytics_workspace_id

  maintenance_window = var.environment == "prod" ? {
    allowed = [{
      day   = "Saturday"
      hours = [22, 23, 0, 1, 2]
    }]
    not_allowed = []
  } : null

  tags = local.common_tags
}

# =============================================================================
# Azure Key Vault - Azure Verified Module v0.9.1
# =============================================================================
module "keyvault" {
  source  = "Azure/avm-res-keyvault-vault/azurerm"
  version = "0.9.1"

  name                = "${local.project_name}-${local.environment}-kv"
  resource_group_name = azurerm_resource_group.main.name
  location            = local.location

  tenant_id = data.azurerm_client_config.current.tenant_id

  sku_name = var.keyvault_sku

  soft_delete_retention_days = 7
  purge_protection_enabled   = var.environment == "prod"
  enable_rbac_authorization  = true

  public_network_access_enabled = true

  tags = local.common_tags
}

data "azurerm_client_config" "current" {}

resource "azurerm_role_assignment" "aks_keyvault_reader" {
  scope                = module.keyvault.resource_id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = module.aks.identity.principal_id
}

resource "azurerm_role_assignment" "current_user_keyvault_admin" {
  scope                = module.keyvault.resource_id
  role_definition_name = "Key Vault Administrator"
  principal_id         = data.azurerm_client_config.current.object_id
}

# =============================================================================
# Azure DNS - Inlined (using existing zone)
# =============================================================================
data "azurerm_dns_zone" "existing" {
  name                = var.dns_zone_name
  resource_group_name = var.dns_resource_group_name
}

resource "azurerm_dns_a_record" "root" {
  count               = var.create_dns_records ? 1 : 0
  name                = "@"
  zone_name           = data.azurerm_dns_zone.existing.name
  resource_group_name = var.dns_resource_group_name
  ttl                 = 300
  records             = [module.aks.ingress_application_gateway[0].public_ip_address]
  tags                = local.common_tags
}

resource "azurerm_dns_a_record" "www" {
  count               = var.create_dns_records ? 1 : 0
  name                = "www"
  zone_name           = data.azurerm_dns_zone.existing.name
  resource_group_name = var.dns_resource_group_name
  ttl                 = 300
  records             = [module.aks.ingress_application_gateway[0].public_ip_address]
  tags                = local.common_tags
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
  value       = module.acr.login_server
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
  value       = module.aks.fqdn
}

output "keyvault_name" {
  description = "Name of the Key Vault"
  value       = module.keyvault.name
}

output "keyvault_uri" {
  description = "URI of the Key Vault"
  value       = module.keyvault.uri
}

output "dns_zone_name" {
  description = "Name of the DNS zone"
  value       = data.azurerm_dns_zone.existing.name
}

output "kube_config_raw" {
  description = "Raw Kubernetes config"
  value       = module.aks.kube_config_raw
  sensitive   = true
}
