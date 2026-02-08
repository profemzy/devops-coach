# =============================================================================
# WackOps-Coach Infrastructure - DEV Environment Variables
# =============================================================================

environment = "dev"
location    = "westus"

# Networking
vnet_address_space = ["10.1.0.0/16"]
subnet_aks_prefix  = "10.1.1.0/24"
subnet_aci_prefix  = "10.1.2.0/24"

# ACR - Use Basic for cost savings in dev
acr_sku = "Basic"

# AKS - Smaller cluster for dev
kubernetes_version    = "1.33.5"
aks_node_count        = 1
aks_node_vm_size      = "Standard_B2s"
aks_min_node_count    = 1
aks_max_node_count    = 2
aks_enable_auto_scaling = true
aks_admin_group_ids   = []

# Key Vault
keyvault_sku = "standard"

# DNS - Use existing zone
dns_zone_name   = "wackops.xyz"
create_dns_zone = false
