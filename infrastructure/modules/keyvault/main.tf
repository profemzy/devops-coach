# =============================================================================
# Key Vault Module
# =============================================================================

# Generate random suffix for unique naming
resource "random_string" "kv_suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "azurerm_key_vault" "main" {
  name                       = "${var.project_name}-${var.environment}-kv"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = var.sku_name
  soft_delete_retention_days = 7
  purge_protection_enabled   = false

  # Enable for deployment and template deployment
  enabled_for_deployment          = true
  enabled_for_template_deployment = true

  # Network access
  public_network_access_enabled = true

  tags = var.tags
}

# Get current client config
data "azurerm_client_config" "current" {}

# =============================================================================
# Access Policy for Current User/Service Principal
# =============================================================================
resource "azurerm_key_vault_access_policy" "current" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = data.azurerm_client_config.current.object_id

  secret_permissions = [
    "Get", "List", "Set", "Delete", "Purge"
  ]
}

# =============================================================================
# Access Policy for AKS Managed Identity
# =============================================================================
resource "azurerm_key_vault_access_policy" "aks" {
  count = var.aks_principal_id != "" ? 1 : 0

  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = var.aks_principal_id

  secret_permissions = [
    "Get", "List"
  ]
}

# =============================================================================
# Sample Secrets (to be populated by application pipeline)
# =============================================================================
# These are placeholders - actual secrets should be set via Azure DevOps pipeline

resource "azurerm_key_vault_secret" "db_password" {
  name         = "postgres-password"
  value        = "PLACEHOLDER-CHANGE-ME"
  key_vault_id = azurerm_key_vault.main.id

  lifecycle {
    ignore_changes = [value]
  }
}

resource "azurerm_key_vault_secret" "secret_key" {
  name         = "flask-secret-key"
  value        = "PLACEHOLDER-CHANGE-ME"
  key_vault_id = azurerm_key_vault.main.id

  lifecycle {
    ignore_changes = [value]
  }
}

# =============================================================================
# Outputs
# =============================================================================
output "id" {
  description = "ID of the Key Vault"
  value       = azurerm_key_vault.main.id
}

output "name" {
  description = "Name of the Key Vault"
  value       = azurerm_key_vault.main.name
}

output "vault_uri" {
  description = "URI of the Key Vault"
  value       = azurerm_key_vault.main.vault_uri
}
