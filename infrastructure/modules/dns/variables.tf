# =============================================================================
# DNS Module - Variables
# =============================================================================

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
}

variable "dns_zone_name" {
  description = "Name of the DNS zone"
  type        = string
}

variable "create_dns_zone" {
  description = "Whether to create a new DNS zone"
  type        = bool
  default     = false
}

variable "aks_ingress_ip" {
  description = "Ingress IP for AKS"
  type        = string
  default     = null
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
