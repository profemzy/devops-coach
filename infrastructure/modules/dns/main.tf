# =============================================================================
# DNS Module - Azure DNS Zone and Records
# =============================================================================

# Use existing DNS zone (recommended - managed separately)
data "azurerm_dns_zone" "existing" {
  count               = var.create_dns_zone ? 0 : 1
  name                = var.dns_zone_name
  resource_group_name = var.resource_group_name
}

# Create new DNS zone (if needed)
resource "azurerm_dns_zone" "new" {
  count               = var.create_dns_zone ? 1 : 0
  name                = var.dns_zone_name
  resource_group_name = var.resource_group_name

  tags = var.tags
}

# A record for root domain (wackops.xyz)
resource "azurerm_dns_a_record" "root" {
  count               = var.aks_ingress_ip != null ? 1 : 0
  name                = "@"
  zone_name           = var.create_dns_zone ? azurerm_dns_zone.new[0].name : data.azurerm_dns_zone.existing[0].name
  resource_group_name = var.resource_group_name
  ttl                 = 300
  records             = [var.aks_ingress_ip]

  tags = var.tags
}

# A record for www (www.wackops.xyz)
resource "azurerm_dns_a_record" "www" {
  count               = var.aks_ingress_ip != null ? 1 : 0
  name                = "www"
  zone_name           = var.create_dns_zone ? azurerm_dns_zone.new[0].name : data.azurerm_dns_zone.existing[0].name
  resource_group_name = var.resource_group_name
  ttl                 = 300
  records             = [var.aks_ingress_ip]

  tags = var.tags
}

# =============================================================================
# Outputs
# =============================================================================
output "zone_name" {
  description = "Name of the DNS zone"
  value       = var.create_dns_zone ? azurerm_dns_zone.new[0].name : data.azurerm_dns_zone.existing[0].name
}

output "zone_id" {
  description = "ID of the DNS zone"
  value       = var.create_dns_zone ? azurerm_dns_zone.new[0].id : data.azurerm_dns_zone.existing[0].id
}

output "name_servers" {
  description = "Name servers for the DNS zone"
  value       = var.create_dns_zone ? azurerm_dns_zone.new[0].name_servers : data.azurerm_dns_zone.existing[0].name_servers
}
