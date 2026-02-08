# =============================================================================
# WackOps-Coach Infrastructure - PROD Environment Variables
# =============================================================================

environment = "prod"
location    = "centralus"

# Networking
vnet_address_space = ["10.4.0.0/16"]
subnet_aks_prefix  = "10.4.1.0/24"
subnet_aci_prefix  = "10.4.2.0/24"

# ACR
acr_sku = "Premium"

# AKS
kubernetes_version      = "1.33.5"
aks_node_count          = 3
aks_node_vm_size        = "Standard_D4s_v3"
aks_min_node_count      = 2
aks_max_node_count      = 10
aks_enable_auto_scaling = true
aks_admin_group_ids     = []

# Key Vault
keyvault_sku = "standard"

# DNS
dns_zone_name           = "wackops.xyz"
dns_resource_group_name = "dns-mgt"
create_dns_records      = true
