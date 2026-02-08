# =============================================================================
# WackOps-Coach Infrastructure - Main Terraform Configuration
# =============================================================================
# This file orchestrates all infrastructure components for the WackOps-Coach
# application running on Azure Kubernetes Service (AKS)
# Using Azure Verified Modules (AVM) where available
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
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }

  # Backend configuration - will be overridden by Azure DevOps
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
# Azure Container Registry (ACR) using Azure Verified Module
# =============================================================================
module "acr" {
  source  = "Azure/avm-res-containerregistry-registry/azurerm"
  version = "0.1.0"

  name                = "${local.project_name}${local.environment}acr"
  resource_group_name = azurerm_resource_group.main.name
  location            = local.location

  sku = var.acr_sku

  # Admin disabled - use managed identity
  admin_enabled = false

  # Trust policy for content trust (Premium only)
  trust_policy_enabled = var.acr_sku == "Premium"

  # Retention policy
  retention_policy = {
    days    = var.acr_sku == "Premium" ? 30 : 7
    enabled = true
  }

  # Public network access
  public_network_access_enabled = true

  tags = local.common_tags
}

# =============================================================================
# Networking Module (Custom - AVM doesn't have full networking module yet)
# =============================================================================
module "networking" {
  source = "../modules/networking"

  resource_group_name = azurerm_resource_group.main.name
  location            = local.location
  environment         = local.environment
  project_name        = local.project_name

  vnet_address_space = var.vnet_address_space
  subnet_aks_prefix  = var.subnet_aks_prefix
  subnet_aci_prefix  = var.subnet_aci_prefix

  tags = local.common_tags
}

# =============================================================================
# Azure Kubernetes Service (AKS) using Azure Verified Module
# =============================================================================
module "aks" {
  source  = "Azure/aks/azurerm"
  version = "9.4.0"

  resource_group_name = azurerm_resource_group.main.name
  location            = local.location

  cluster_name = "${local.resource_prefix}-aks"
  prefix       = local.project_name

  # Kubernetes version
  kubernetes_version  = var.kubernetes_version
  orchestrator_version = var.kubernetes_version
  sku_tier            = var.environment == "prod" ? "Standard" : "Free"

  # System node pool
  agents_pool_name    = "system"
  agents_count        = var.aks_node_count
  agents_size         = var.aks_node_vm_size
  agents_min_count    = var.aks_min_node_count
  agents_max_count    = var.aks_max_node_count
  enable_auto_scaling = var.aks_enable_auto_scaling

  # Use Azure CNI with dynamic IP allocation
  vnet_subnet_id = module.networking.aks_subnet_id

  # Network profile
  network_plugin  = "azure"
  network_policy  = "calico"
  load_balancer_sku = "standard"

  # Enable OIDC and Workload Identity for modern authentication
  oidc_issuer_enabled       = true
  workload_identity_enabled = true

  # Azure RBAC for Kubernetes
  rbac_aad_managed = true
  rbac_aad_admin_group_object_ids = var.aks_admin_group_ids

  # Attach ACR
  attached_acr_id_map = {
    main = module.acr.resource_id
  }

  # Monitoring
  log_analytics_workspace_enabled = var.log_analytics_workspace_id != null
  log_analytics_workspace_id      = var.log_analytics_workspace_id

  # Maintenance window for production
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
# Azure Key Vault using Azure Verified Module
# =============================================================================
module "keyvault" {
  source  = "Azure/avm-res-keyvault-vault/azurerm"
  version = "0.9.1"

  name                = "${local.project_name}-${local.environment}-kv"
  resource_group_name = azurerm_resource_group.main.name
  location            = local.location

  tenant_id = data.azurerm_client_config.current.tenant_id

  sku_name = var.keyvault_sku

  # Soft delete and purge protection
  soft_delete_retention_days = 7
  purge_protection_enabled   = var.environment == "prod" # Enable in prod only

  # Access policies - using RBAC instead of access policies for better security
  enable_rbac_authorization = true

  # Network access
  public_network_access_enabled = true

  tags = local.common_tags
}

# Get current client config
data "azurerm_client_config" "current" {}

# Grant AKS managed identity access to Key Vault
resource "azurerm_role_assignment" "aks_keyvault_reader" {
  scope                = module.keyvault.resource_id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = module.aks.identity.principal_id
}

# Grant current user admin access to Key Vault
resource "azurerm_role_assignment" "current_user_keyvault_admin" {
  scope                = module.keyvault.resource_id
  role_definition_name = "Key Vault Administrator"
  principal_id         = data.azurerm_client_config.current.object_id
}

# =============================================================================
# Azure DNS (for wackops.xyz)
# =============================================================================
module "dns" {
  source = "../modules/dns"

  resource_group_name = azurerm_resource_group.main.name
  environment         = local.environment
  project_name        = local.project_name

  # Use existing DNS zone
  dns_zone_name   = var.dns_zone_name
  create_dns_zone = var.create_dns_zone

  # AKS ingress IP
  aks_ingress_ip = module.aks.ingress_application_gateway != null ? module.aks.ingress_application_gateway[0].public_ip_address : null

  tags = local.common_tags
}

# =============================================================================
# Outputs
# =============================================================================
output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "resource_group_id" {
  description = "ID of the resource group"
  value       = azurerm_resource_group.main.id
}

output "aks_cluster_name" {
  description = "Name of the AKS cluster"
  value       = module.aks.aks_name
}

output "aks_cluster_fqdn" {
  description = "FQDN of the AKS cluster"
  value       = module.aks.fqdn
}

output "acr_login_server" {
  description = "Login server for ACR"
  value       = module.acr.login_server
}

output "acr_name" {
  description = "Name of the ACR"
  value       = module.acr.name
}

output "keyvault_name" {
  description = "Name of the Key Vault"
  value       = module.keyvault.name
}

output "keyvault_uri" {
  description = "URI of the Key Vault"
  value       = module.keyvault.uri
}

output "keyvault_resource_id" {
  description = "Resource ID of the Key Vault"
  value       = module.keyvault.resource_id
}

output "vnet_id" {
  description = "ID of the Virtual Network"
  value       = module.networking.vnet_id
}

output "aks_subnet_id" {
  description = "ID of the AKS subnet"
  value       = module.networking.aks_subnet_id
}

output "kube_config_raw" {
  description = "Raw Kubernetes config"
  value       = module.aks.kube_config_raw
  sensitive   = true
}
