# =============================================================================
# WackOps-Coach Infrastructure - Variables
# =============================================================================

# =============================================================================
# General Variables
# =============================================================================
variable "environment" {
  description = "Environment name (dev, qa, stage, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "qa", "stage", "prod"], var.environment)
    error_message = "Environment must be one of: dev, qa, stage, prod."
  }
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "centralus"
}

# =============================================================================
# Networking Variables
# =============================================================================
variable "vnet_address_space" {
  description = "Address space for the Virtual Network"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "subnet_aks_prefix" {
  description = "Address prefix for AKS subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "subnet_aci_prefix" {
  description = "Address prefix for ACI subnet (virtual nodes)"
  type        = string
  default     = "10.0.2.0/24"
}

# =============================================================================
# ACR Variables
# =============================================================================
variable "acr_sku" {
  description = "SKU for Azure Container Registry"
  type        = string
  default     = "Standard"

  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.acr_sku)
    error_message = "ACR SKU must be one of: Basic, Standard, Premium."
  }
}

# =============================================================================
# AKS Variables
# =============================================================================
variable "kubernetes_version" {
  description = "Kubernetes version for AKS"
  type        = string
  default     = "1.33.5"
}

variable "aks_node_count" {
  description = "Initial node count for AKS"
  type        = number
  default     = 2
}

variable "aks_node_vm_size" {
  description = "VM size for AKS nodes"
  type        = string
  default     = "Standard_B2s"
}

variable "aks_min_node_count" {
  description = "Minimum node count for auto-scaling"
  type        = number
  default     = 1
}

variable "aks_max_node_count" {
  description = "Maximum node count for auto-scaling"
  type        = number
  default     = 5
}

variable "aks_enable_auto_scaling" {
  description = "Enable cluster auto-scaler"
  type        = bool
  default     = true
}

variable "aks_admin_group_ids" {
  description = "List of Azure AD group object IDs for AKS admins"
  type        = list(string)
  default     = []
}

# =============================================================================
# Key Vault Variables
# =============================================================================
variable "keyvault_sku" {
  description = "SKU for Azure Key Vault"
  type        = string
  default     = "standard"

  validation {
    condition     = contains(["standard", "premium"], var.keyvault_sku)
    error_message = "Key Vault SKU must be standard or premium."
  }
}

# =============================================================================
# DNS Variables
# =============================================================================
variable "dns_zone_name" {
  description = "Name of the DNS zone"
  type        = string
  default     = "wackops.xyz"
}

variable "create_dns_zone" {
  description = "Whether to create a new DNS zone or use existing"
  type        = bool
  default     = false
}

# =============================================================================
# Monitoring Variables
# =============================================================================
variable "log_analytics_workspace_id" {
  description = "ID of Log Analytics workspace for monitoring (optional)"
  type        = string
  default     = null
}
