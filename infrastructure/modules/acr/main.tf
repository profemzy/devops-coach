# =============================================================================
# ACR Module - Azure Container Registry
# =============================================================================

resource "azurerm_container_registry" "main" {
  name                = "${var.project_name}${var.environment}acr"
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = var.sku
  admin_enabled       = var.admin_enabled

  # Trust policy for content trust
  trust_policy {
    enabled = var.sku == "Premium" ? true : false
  }

  # Data endpoint for Premium SKU
  dynamic "data_endpoint_enabled" {
    for_each = var.sku == "Premium" ? [1] : []
    content {
      # This is a boolean attribute in azurerm provider 3.x
    }
  }

  # Retention policy
  retention_policy {
    days    = var.sku == "Premium" ? 30 : 7
    enabled = true
  }

  # Public network access
  public_network_access_enabled = true

  tags = var.tags
}

# =============================================================================
# Outputs
# =============================================================================
output "acr_id" {
  description = "ID of the ACR"
  value       = azurerm_container_registry.main.id
}

output "name" {
  description = "Name of the ACR"
  value       = azurerm_container_registry.main.name
}

output "login_server" {
  description = "Login server URL"
  value       = azurerm_container_registry.main.login_server
}

output "admin_username" {
  description = "Admin username (if enabled)"
  value       = var.admin_enabled ? azurerm_container_registry.main.admin_username : null
}

output "admin_password" {
  description = "Admin password (if enabled)"
  value       = var.admin_enabled ? azurerm_container_registry.main.admin_password : null
  sensitive   = true
}
