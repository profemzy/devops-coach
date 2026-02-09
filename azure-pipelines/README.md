# Azure DevOps Pipelines for WackOps-Coach Application

This directory contains Azure DevOps pipeline configurations for the **WackOps-Coach application deployment**.

> **Note:** Infrastructure pipelines (Terraform for AKS, ACR, Key Vault) are located in the [infotitans-azure](https://github.com/profemzy/infotitans-azure) repository.

## Pipeline Architecture

| Pipeline | Purpose | Trigger | File |
|----------|---------|---------|------|
| **01-App-CI** | Build & push Docker image | Push to `devopscoach/**` | `01-app-ci.yml` |
| **02-App-CD** | Deploy to AKS (DEV → PROD) | CI success or manual | `02-app-cd.yml` |

## Separation of Concerns

```
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE (infotitans-azure)              │
│  • AKS Clusters, ACR, Key Vault, VNet, DNS                       │
│  • Managed by: Terraform via Azure DevOps                        │
│  • Pipelines: 01/02-Infrastructure-CI/CD                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION (devops-coach)                     │
│  • Docker image build & push to ACR                              │
│  • Kubernetes manifest deployment                                │
│  • Managed by: 01-App-CI → 02-App-CD                            │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

### 1. Service Connections

#### Azure Container Registry
- **Name**: `wackops-acr-connection`
- **Registry**: `wackopscoachdevacr` (dev) / `wackopscoachprodacr` (prod)

#### AKS Connection
- **Name**: `wackops-aks-connection`
- **DEV Cluster**: `wackopscoach-dev-aks`
- **PROD Cluster**: `wackopscoach-prod-aks`

### 2. Environments

Create in **Pipelines → Environments**:
- `dev` - No approval required
- `prod` - Requires approval before deployment

## Pipeline Setup

### 01-App-CI Pipeline

1. Go to **Pipelines** → **New Pipeline**
2. Select **GitHub** → `profemzy/devops-coach`
3. Path: `/azure-pipelines/01-app-ci.yml`
4. Rename to: `01-App-CI`
5. Save

### 02-App-CD Pipeline

1. Go to **Pipelines** → **New Pipeline**
2. Select **GitHub** → `profemzy/devops-coach`
3. Path: `/azure-pipelines/02-app-cd.yml`
4. Rename to: `02-App-CD`
5. Save

## Deployment Flow

### Automatic Deployment (CI → CD)

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Push to   │───▶│   01-App-CI │───▶│   02-App-CD │───▶│   [APPROVE] │───▶│
│   master    │    │   Build     │    │   DEV Auto  │    │   PROD      │
│             │    │   Push ACR  │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                              │
                                                              ▼
                                                    https://wackops.xyz
```

### Manual Deployment

You can also run **02-App-CD** manually:
1. Go to **Pipelines** → `02-App-CD`
2. Click **Run pipeline**
3. Select parameters:
   - `imageTag`: Specific tag to deploy (default: `latest`)
   - `deployDev`: ✅/❌
   - `deployProd`: ✅/❌
4. Click **Run**

## URLs

| Environment | URL | Ingress Manifest |
|-------------|-----|------------------|
| **DEV** | https://dev.wackops.xyz | `k8s/dev/ingress.yaml` |
| **PROD** | https://wackops.xyz | `k8s/prod/ingress.yaml` |

## Manifest Structure

```
k8s/
├── dev/                    # DEV environment
│   ├── namespace.yaml
│   ├── redis.yaml
│   ├── secret.yaml         # Update with DEV secrets
│   ├── migration-job.yaml
│   ├── deployment.yaml
│   ├── worker-deployment.yaml
│   ├── service.yaml
│   └── ingress.yaml        # dev.wackops.xyz
└── prod/                   # PROD environment
    ├── namespace.yaml
    ├── redis.yaml
    ├── secret.yaml         # Update with PROD secrets
    ├── migration-job.yaml
    ├── deployment.yaml
    ├── worker-deployment.yaml
    ├── service.yaml
    └── ingress.yaml        # wackops.xyz
```

## Important: Update Secrets

Before first deployment, update secrets in both environments:

```bash
# DEV secrets
cp k8s/dev/secret.yaml k8s/dev/secret.yaml.backup
# Edit k8s/dev/secret.yaml with base64-encoded DEV secrets

# PROD secrets  
cp k8s/prod/secret.yaml k8s/prod/secret.yaml.backup
# Edit k8s/prod/secret.yaml with base64-encoded PROD secrets
```

**Never commit actual secrets to Git!**

## Troubleshooting

### Pipeline not triggering
- Check CI pipeline completed successfully
- Verify branch filters match
- Check resource trigger is enabled in CD pipeline

### Deployment failures
- Verify service connections are valid
- Check AKS cluster is accessible
- Review pod logs: `kubectl logs -n wackops-coach deployment/wackops-coach`

### Image pull errors
- Verify ACR is attached to AKS: `az aks show --name wackopscoach-dev-aks --resource-group wackopscoach-dev-rg --query agentPoolProfiles[0].count`

## Related Repositories

- **Application Code**: [profemzy/devops-coach](https://github.com/profemzy/devops-coach) (this repo)
- **Infrastructure**: [profemzy/infotitans-azure](https://github.com/profemzy/infotitans-azure)
