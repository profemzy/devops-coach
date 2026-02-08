# Azure DevOps Pipelines for WackOps-Coach

This directory contains Azure DevOps pipeline configurations for deploying the WackOps-Coach **application**.

> **Note:** Infrastructure pipelines (Terraform for AKS, ACR, Key Vault) are located in the [infotitans-azure](https://github.com/profemzy/infotitans-azure) repository under `terraform/wackops-coach/`.

## Overview

| Pipeline | Purpose | File | Repository |
|----------|---------|------|------------|
| **01-infrastructure-ci** | Validate Terraform code, plan all environments | `01-infrastructure-ci.yml` | [infotitans-azure](https://github.com/profemzy/infotitans-azure) |
| **02-infrastructure-cd** | Deploy infrastructure to DEV/PROD with approvals | `02-infrastructure-cd.yml` | [infotitans-azure](https://github.com/profemzy/infotitans-azure) |
| **03-app-deployment** | Build Docker image, deploy to AKS (DEV → PROD) | `03-app-deployment.yml` | This repo |

## Prerequisites

### 1. Azure DevOps Organization
- Create or use existing Azure DevOps organization
- Create a project named `wackops-coach`

### 2. Service Connections

#### Azure Container Registry
1. Go to **Project Settings** → **Service Connections**
2. Click **New Service Connection** → **Docker Registry**
3. Select **Azure Container Registry**
4. Enter:
   - **Subscription**: Your Azure subscription
   - **Azure Container Registry**: `wackopscoachdevacr` (dev) or `wackopscoachprodacr` (prod)
   - **Service Connection Name**: `wackops-acr-connection`
5. Click **Save**

#### AKS Connection
1. Go to **Project Settings** → **Service Connections**
2. Click **New Service Connection** → **Kubernetes**
3. Select **Azure Subscription**
4. Enter:
   - **Subscription**: Your Azure subscription
   - **Cluster Name**: `wackopscoach-dev-aks` or `wackopscoach-prod-aks`
   - **Namespace**: `wackops-coach`
   - **Service Connection Name**: `wackops-aks-connection`
5. Click **Save**

## Pipeline Setup

### App Deployment Pipeline

1. Go to **Pipelines** → **New Pipeline**
2. Select **GitHub** → Select `profemzy/devops-coach` repository
3. Path: `/azure-pipelines/03-app-deployment.yml`
4. Click **Save**
5. Rename to: `03-App-Deployment`

## Usage

### Deploy Application

Application deployment is triggered when code changes:

```bash
# Push application changes
git add devopscoach/
git commit -m "Add new feature"
git push origin master
```

**Flow:**
1. Build and push Docker image to ACR
2. Deploy to DEV AKS automatically
3. Wait for approval to deploy to PROD

### Manual Deployment

To deploy manually (e.g., hotfix):

1. Go to **Pipelines** → Select `03-App-Deployment`
2. Click **Run pipeline**
3. Select branch
4. Click **Run**

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Push to       │────▶│   Build Image   │────▶│   Deploy DEV    │
│   devopscoach/  │     │   Push to ACR   │     │   Run Migration │
│                 │     │                 │     │   Verify        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │   [APPROVE]     │
                                               │   Deploy PROD   │
                                               │   Verify        │
                                               └─────────────────┘
```

## Resources Created by Infrastructure (infotitans-azure)

| Resource | DEV | PROD |
|----------|-----|------|
| **Resource Group** | wackopscoach-dev-rg | wackopscoach-prod-rg |
| **AKS Cluster** | wackopscoach-dev-aks | wackopscoach-prod-aks |
| **ACR** | wackopscoachdevacr | wackopscoachprodacr |
| **Key Vault** | wackopscoach-dev-kv | wackopscoach-prod-kv |
| **VNet** | wackopscoach-dev-vnet | wackopscoach-prod-vnet |

## Admin Access

The AKS clusters are configured with the following admin group:

- **Group**: `wackops-prod-cluster-administrators`
- **Object ID**: `78d4fae8-1c98-49c4-9d39-d6eb84b35121`

Members of this group have cluster-admin access to both DEV and PROD AKS clusters.

## Troubleshooting

### Pipeline Failures

Check the following:
1. Service connections are valid and not expired
2. Azure subscription has sufficient permissions
3. Resource quotas are not exceeded
4. AKS cluster is healthy

### Rollback

For application rollback:
1. Go to previous pipeline run
2. Click **Run new** with previous commit
3. Or re-run previous successful deployment

## Security Best Practices

1. **Use OIDC authentication** - No secrets stored in pipeline
2. **Environment approvals** - Require approval for prod
3. **RBAC** - Use least privilege access
4. **Secrets in Key Vault** - Never hardcode secrets
5. **Branch policies** - Require PR reviews for main branch

## Related Repositories

- **Application**: [profemzy/devops-coach](https://github.com/profemzy/devops-coach) (this repo)
- **Infrastructure**: [profemzy/infotitans-azure](https://github.com/profemzy/infotitans-azure) (Terraform for AKS, ACR, Key Vault)
