# =============================================================================
# AKS Module - Azure Kubernetes Service
# =============================================================================

# Generate random suffix for unique naming
resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

# =============================================================================
# AKS Cluster
# =============================================================================
resource "azurerm_kubernetes_cluster" "main" {
  name                = "${var.project_name}-${var.environment}-aks"
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = "${var.project_name}-${var.environment}"
  kubernetes_version  = var.kubernetes_version
  
  # Identity - System assigned for simplicity
  identity {
    type = "SystemAssigned"
  }

  # Default node pool
  default_node_pool {
    name                = "default"
    node_count          = var.node_count
    vm_size             = var.node_vm_size
    vnet_subnet_id      = var.vnet_subnet_id
    enable_auto_scaling = var.enable_auto_scaling
    min_count           = var.enable_auto_scaling ? var.min_node_count : null
    max_count           = var.enable_auto_scaling ? var.max_node_count : null
    
    # Node labels and tags
    node_labels = {
      environment = var.environment
      nodepool    = "default"
    }
    
    tags = var.tags
  }

  # Network profile - Azure CNI for advanced networking
  network_profile {
    network_plugin     = "azure"
    network_policy     = "calico"
    load_balancer_sku  = "standard"
    service_cidr       = "10.100.0.0/16"
    dns_service_ip     = "10.100.0.10"
    docker_bridge_cidr = "172.17.0.1/16"
  }

  # Enable features
  azure_policy_enabled = true
  http_application_routing_enabled = false

  # RBAC
  role_based_access_control_enabled = true

  # Monitoring
  dynamic "oms_agent" {
    for_each = var.log_analytics_workspace_id != null ? [1] : []
    content {
      log_analytics_workspace_id = var.log_analytics_workspace_id
    }
  }

  # Ingress controller (nginx) - will be installed via Helm/Kubectl
  # Cert-manager for TLS - will be installed separately

  tags = var.tags

  lifecycle {
    ignore_changes = [
      default_node_pool[0].node_count, # Ignore changes from auto-scaler
    ]
  }
}

# =============================================================================
# ACR Pull Role Assignment
# =============================================================================
resource "azurerm_role_assignment" "acr_pull" {
  scope                = var.acr_id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_kubernetes_cluster.main.kubelet_identity[0].object_id
}

# =============================================================================
# Managed NGINX Ingress Controller via Helm (optional)
# =============================================================================
# This creates a Public IP for the ingress controller
resource "azurerm_public_ip" "ingress" {
  name                = "${var.project_name}-${var.environment}-ingress-ip"
  resource_group_name = azurerm_kubernetes_cluster.main.node_resource_group
  location            = var.location
  allocation_method   = "Static"
  sku                 = "Standard"
  
  domain_name_label = "${var.project_name}-${var.environment}"
  
  tags = var.tags
}

# =============================================================================
# Outputs
# =============================================================================
output "cluster_name" {
  description = "Name of the AKS cluster"
  value       = azurerm_kubernetes_cluster.main.name
}

output "cluster_id" {
  description = "ID of the AKS cluster"
  value       = azurerm_kubernetes_cluster.main.id
}

output "cluster_fqdn" {
  description = "FQDN of the AKS cluster"
  value       = azurerm_kubernetes_cluster.main.fqdn
}

output "kube_config" {
  description = "Raw Kubernetes config"
  value       = azurerm_kubernetes_cluster.main.kube_config_raw
  sensitive   = true
}

output "host" {
  description = "Kubernetes host"
  value       = azurerm_kubernetes_cluster.main.kube_config[0].host
  sensitive   = true
}

output "client_certificate" {
  description = "Kubernetes client certificate"
  value       = azurerm_kubernetes_cluster.main.kube_config[0].client_certificate
  sensitive   = true
}

output "client_key" {
  description = "Kubernetes client key"
  value       = azurerm_kubernetes_cluster.main.kube_config[0].client_key
  sensitive   = true
}

output "cluster_ca_certificate" {
  description = "Kubernetes cluster CA certificate"
  value       = azurerm_kubernetes_cluster.main.kube_config[0].cluster_ca_certificate
  sensitive   = true
}

output "kubelet_identity_object_id" {
  description = "Object ID of the kubelet identity"
  value       = azurerm_kubernetes_cluster.main.kubelet_identity[0].object_id
}

output "ingress_ip" {
  description = "Public IP address for ingress controller"
  value       = azurerm_public_ip.ingress.ip_address
}

output "ingress_ip_fqdn" {
  description = "FQDN of the ingress IP"
  value       = azurerm_public_ip.ingress.fqdn
}
