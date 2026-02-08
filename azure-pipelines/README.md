# Azure DevOps Pipelines for WackOps-Coach

This directory contains Azure DevOps pipeline configurations for deploying the WackOps-Coach infrastructure and application.

## Overview

| Pipeline | Purpose | File |
|----------|---------|------|
| **01-infrastructure-ci** | Validate Terraform code, plan all environments | `01-infrastructure-ci.yml` |
| **02-infrastructure-cd** | Deploy infrastructure to DEV/PROD with approvals | `02-infrastructure-cd.yml` |
| **03-app-deployment** | Build Docker image, deploy to AKS (DEV → PROD) | `03-app-deployment.yml` |

## Prerequisites

### 1. Azure DevOps Organization
- Create or use existing Azure DevOps organization
- Create a project named `wackops-coach`

### 2. Service Connections

#### Azure Resource Manager (OIDC - Recommended)
1. Go to **Project Settings** → **Service Connections**
2. Click **New Service Connection** → **Azure Resource Manager**
3. Select **Workload Identity Federation (automatic)**
4. Enter:
   - **Subscription**: Your Azure subscription
   - **Resource Group**: (optional, leave empty for all)
   - **Service Connection Name**: `terraformiacdevops1`
5. Click **Save**

#### Azure Container Registry
1. Go to **Project Settings** → **Service Connections**
2. Click **New Service Connection** → **Docker Registry**
3. Select **Azure Container Registry**
4. Enter:
   - **Subscription**: Your Azure subscription
   - **Azure Container Registry**: Select or enter your ACR name
   - **Service Connection Name**: `wackops-acr-connection`
5. Click **Save**

#### AKS Connection
1. Go to **Project Settings** → **Service Connections**
2. Click **New Service Connection** → **Kubernetes**
3. Select **Azure Subscription**
4. Enter:
   - **Subscription**: Your Azure subscription
   - **Cluster Name**: Select your AKS cluster
   - **Namespace**: `wackops-coach`
   - **Service Connection Name**: `wackops-aks-connection`
5. Click **Save**

### 3. Storage Account for Terraform State

```bash
# Create Resource Group for Terraform state
az group create --name terraform-storage-rg --location centralus

# Create Storage Account
az storage account create \
  --name terraformstatewakopsaks \
  --resource-group terraform-storage-rg \
  --location centralus \
  --sku Standard_LRS \
  --kind StorageV2

# Create Container
az storage container create \
  --name tfstatefiles \
  --account-name terraformstatewakopsaks
```

### 4. Environments and Approvals

Create environments for deployment approvals:

1. Go to **Pipelines** → **Environments**
2. Create the following environments:
   - `dev` - No approval required
   - `prod` - Requires approval

3. For **prod** environment:
   - Click on `prod` → **Approvals and checks**
   - Click **Approvals**
   - Add approvers (users/groups)
   - Set **Timeout**: 30 days
   - Click **Create**

## Pipeline Setup

### Step 1: Infrastructure CI Pipeline

1. Go to **Pipelines** → **New Pipeline**
2. Select **GitHub** → Select `profemzy/devops-coach` repository
3. Select **Existing Azure Pipelines YAML file**
4. Path: `/azure-pipelines/01-infrastructure-ci.yml`
5. Click **Save** (don't run yet)
6. Rename to: `01-Infrastructure-CI`

### Step 2: Infrastructure CD Pipeline

1. Go to **Pipelines** → **New Pipeline**
2. Select **GitHub** → Select repository
3. Path: `/azure-pipelines/02-infrastructure-cd.yml`
4. Click **Save**
5. Rename to: `02-Infrastructure-CD`

### Step 3: App Deployment Pipeline

1. Go to **Pipelines** → **New Pipeline**
2. Select **GitHub** → Select repository
3. Path: `/azure-pipelines/03-app-deployment.yml`
4. Click **Save**
5. Rename to: `03-App-Deployment`

## Usage

### Deploy Infrastructure

Infrastructure deployment is triggered automatically when changes are pushed to `infrastructure/` folder:

```bash
# Push changes to infrastructure
git add infrastructure/
git commit -m "Update AKS configuration"
git push origin master
```

**Flow:**
1. CI Pipeline runs (validate, plan all environments)
2. CD Pipeline triggers automatically
3. DEV environment deploys automatically
4. PROD environment waits for approval

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

1. Go to **Pipelines** → Select pipeline
2. Click **Run pipeline**
3. Select branch
4. For infrastructure: Select environments to deploy
5. Click **Run**

## Pipeline Variables

### Common Variables (Set in Pipeline Settings)

| Variable | Description | Default |
|----------|-------------|---------|
| `tf_version` | Terraform version | `1.10.0` |
| `azureServiceConnection` | Azure service connection name | `terraformiacdevops1` |
| `backendResourceGroup` | Terraform state resource group | `terraform-storage-rg` |
| `backendStorageAccount` | Terraform state storage account | `terraformstatewakopsaks` |
| `backendContainerName` | Terraform state container | `tfstatefiles` |
| `acrLoginServer` | ACR login server | `wackopscoachprodacr.azurecr.io` |

### Setting Pipeline Variables

1. Go to **Pipelines** → Select pipeline
2. Click **Edit** → **Variables**
3. Add or modify variables
4. Mark sensitive variables as **Secret**

## Architecture

### Infrastructure Deployment

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Push to       │────▶│   CI Pipeline   │────▶│   CD Pipeline   │
│   infrastructure│     │   - Validate    │     │   - DEV Auto    │
│                 │     │   - Plan        │     │   - PROD Approve│
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         │
                    ┌────────────────────────────────────┼────┐
                    ▼                                    ▼    ▼
            ┌──────────────┐                      ┌──────────────┐
            │   DEV AKS    │                      │   PROD AKS   │
            │   + ACR      │                      │   + ACR      │
            │   + KeyVault │                      │   + KeyVault │
            └──────────────┘                      └──────────────┘
```

### Application Deployment

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

## Troubleshooting

### Terraform State Lock

If a deployment fails and state is locked:

```bash
# Get storage account key
az storage account keys list \
  --account-name terraformstatewakopsaks \
  --query '[0].value' -o tsv

# Remove lock
az storage blob lease break \
  --blob-name dev-terraform.tfstate \
  --container-name tfstatefiles \
  --account-name terraformstatewakopsaks
```

### Pipeline Failures

Check the following:
1. Service connections are valid and not expired
2. Azure subscription has sufficient permissions
3. Resource quotas are not exceeded
4. Terraform state storage is accessible

### Rollback

For infrastructure rollback:
1. Go to previous pipeline run
2. Click **Run new** with previous commit
3. For application: Re-run previous successful deployment

## Security Best Practices

1. **Use OIDC authentication** - No secrets stored in pipeline
2. **Environment approvals** - Require approval for prod
3. **Separate pipelines** - CI/CD and app deployment are separate
4. **RBAC** - Use least privilege access
5. **Secrets in Key Vault** - Never hardcode secrets
6. **Branch policies** - Require PR reviews for main branch

## Support

For issues:
- Check pipeline logs in Azure DevOps
- Review Terraform state in Azure Storage
- Verify service connection permissions
- Check AKS cluster health
