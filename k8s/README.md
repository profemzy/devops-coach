# Kubernetes Deployment

This directory contains Kubernetes manifests for deploying the WackOps-Coach application.

🌐 **Production URL:** https://wackops.xyz  
Powered by [InfoTitans](https://infotitans.com/)

## Setup Instructions

### 1. Create Secrets

Copy the example secret file and fill in your values:

```bash
cp secret.yaml.example secret.yaml
```

Then encode your sensitive values to base64:

```bash
# Example: Encode a value
echo -n "your-actual-value" | base64

# Example: Decode a value (to verify)
echo "base64-encoded-value" | base64 -d
```

Update `secret.yaml` with your base64-encoded values:
- `OPENAI_API_BASE` - Your OpenAI-compatible API endpoint
- `OPENAI_API_KEY` - Your OpenAI API key
- `OPENAI_MODEL` - Model name (e.g., gpt-4, claude-haiku-4-5)
- `POSTGRES_DB` - PostgreSQL database name
- `POSTGRES_HOST` - PostgreSQL server hostname
- `POSTGRES_PASSWORD` - PostgreSQL password
- `POSTGRES_PORT` - PostgreSQL port (usually 5432)
- `POSTGRES_USER` - PostgreSQL username
- `REDIS_URL` - Redis connection URL
- `SECRET_KEY` - Flask secret key (generate with `./run flask secrets`)
- `TAVILY_API_KEY` - Tavily web search API key

⚠️ **IMPORTANT**: `secret.yaml` is gitignored and should NEVER be committed to version control!

### 2. Deploy to Kubernetes

Apply the manifests in the following order:

```bash
# Create namespace
kubectl apply -f namespace.yaml

# Create secrets
kubectl apply -f secret.yaml

# Deploy Redis
kubectl apply -f redis.yaml

# Run database migrations (one-time job)
kubectl apply -f migration-job.yaml

# Wait for migration to complete
kubectl wait --for=condition=complete --timeout=300s job/devops-coach-migration -n devops-coach

# Deploy application
kubectl apply -f deployment.yaml

# Create service
kubectl apply -f service.yaml

# Create ingress (optional, for external access)
kubectl apply -f ingress.yaml
```

### 3. Verify Deployment

```bash
# Check all resources
kubectl get all -n devops-coach

# Check pod logs
kubectl logs -f deployment/devops-coach -n devops-coach

# Check migration job logs
kubectl logs job/devops-coach-migration -n devops-coach
```

## Updating the Application

### Update Docker Image

```bash
# Build and push new image
./build_and_push.sh

# Restart deployment to pull new image
kubectl rollout restart deployment/devops-coach -n devops-coach

# Watch rollout status
kubectl rollout status deployment/devops-coach -n devops-coach
```

### Update Secrets

```bash
# Edit secrets
kubectl edit secret devops-coach-secrets -n devops-coach

# Or re-apply the secret file
kubectl apply -f secret.yaml

# Restart deployment to pick up new secrets
kubectl rollout restart deployment/devops-coach -n devops-coach
```

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n devops-coach
kubectl describe pod <pod-name> -n devops-coach
```

### View Logs

```bash
kubectl logs -f deployment/devops-coach -n devops-coach
```

### Access Pod Shell

```bash
kubectl exec -it deployment/devops-coach -n devops-coach -- bash
```

### Database Connection Issues

```bash
# Test database connection from pod
kubectl exec -it deployment/devops-coach -n devops-coach -- bash
# Inside pod:
psql -h <postgres-host> -U <postgres-user> -d <postgres-db>
```

## Resource Requirements

Current configuration:
- **CPU**: 200m request, 500m limit
- **Memory**: 256Mi request, 512Mi limit

Adjust in `deployment.yaml` based on your needs.

## Health Checks

- **Liveness Probe**: `/up` endpoint (every 30s)
- **Readiness Probe**: `/up` endpoint (every 10s)
