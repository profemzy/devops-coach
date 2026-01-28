#!/bin/bash
set -e

# Deployment script for DevOps Coach to AKS
# Usage: ./deploy.sh [build|deploy|all]

REGISTRY="prodacrva1ng1.azurecr.io"
IMAGE_NAME="devops-coach"
TAG="latest"
FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${TAG}"
NAMESPACE="devops-coach"

echo "=========================================="
echo "DevOps Coach Kubernetes Deployment"
echo "=========================================="

# Function to build and push Docker image
build_and_push() {
    echo ""
    echo "📦 Building Docker image..."
    echo "   Target: ${FULL_IMAGE_NAME}"
    docker build --platform linux/amd64 --target app -t "${FULL_IMAGE_NAME}" .
    
    echo ""
    echo "📤 Pushing to ACR..."
    docker push "${FULL_IMAGE_NAME}"
    
    echo ""
    echo "✅ Image built and pushed successfully!"
}

# Function to deploy to Kubernetes
deploy_to_k8s() {
    echo ""
    echo "☸️  Deploying to AKS..."
    
    # Check if kubectl is configured
    if ! kubectl cluster-info > /dev/null 2>&1; then
        echo "❌ Error: kubectl is not configured or cannot connect to cluster"
        exit 1
    fi
    
    echo ""
    echo "📋 Applying Kubernetes manifests..."
    
    # Create namespace if it doesn't exist
    kubectl apply -f k8s/namespace.yaml
    
    # Check if secrets exist
    if ! kubectl get secret devops-coach-secrets -n ${NAMESPACE} > /dev/null 2>&1; then
        echo ""
        echo "⚠️  Warning: Secrets not found!"
        echo "   Please create secrets first:"
        echo "   cp k8s/secret.yaml.example k8s/secret.yaml"
        echo "   # Edit k8s/secret.yaml with your values"
        echo "   kubectl apply -f k8s/secret.yaml"
        echo ""
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Apply manifests
    kubectl apply -f k8s/secret.yaml 2>/dev/null || echo "   Secrets already exist"
    kubectl apply -f k8s/redis.yaml
    kubectl apply -f k8s/deployment.yaml
    kubectl apply -f k8s/worker-deployment.yaml
    kubectl apply -f k8s/service.yaml
    kubectl apply -f k8s/ingress.yaml
    
    echo ""
    echo "⏳ Waiting for rollout to complete..."
    kubectl rollout status deployment/devops-coach -n ${NAMESPACE} --timeout=300s
    kubectl rollout status deployment/devops-coach-worker -n ${NAMESPACE} --timeout=300s
    
    echo ""
    echo "✅ Deployment completed successfully!"
}

# Function to run database migrations
run_migrations() {
    echo ""
    echo "🗄️  Running database migrations..."
    
    # Apply migration job
    kubectl apply -f k8s/migration-job.yaml
    
    # Wait for migration to complete
    echo "   Waiting for migration job to complete..."
    kubectl wait --for=condition=complete --timeout=300s job/devops-coach-migration -n ${NAMESPACE}
    
    echo ""
    echo "✅ Migrations completed!"
}

# Function to show deployment status
show_status() {
    echo ""
    echo "📊 Deployment Status:"
    echo "=========================================="
    kubectl get all -n ${NAMESPACE}
    
    echo ""
    echo "🌐 Application URL:"
    echo "   https://devops.infotitans.com"
    
    echo ""
    echo "📋 Useful commands:"
    echo "   View logs:        kubectl logs -f deployment/devops-coach -n ${NAMESPACE}"
    echo "   Worker logs:      kubectl logs -f deployment/devops-coach-worker -n ${NAMESPACE}"
    echo "   Pod shell:        kubectl exec -it deployment/devops-coach -n ${NAMESPACE} -- bash"
    echo "   Restart app:      kubectl rollout restart deployment/devops-coach -n ${NAMESPACE}"
}

# Main script logic
case "${1:-all}" in
    build)
        build_and_push
        ;;
    deploy)
        deploy_to_k8s
        show_status
        ;;
    migrate)
        run_migrations
        ;;
    all)
        build_and_push
        deploy_to_k8s
        show_status
        ;;
    *)
        echo "Usage: $0 [build|deploy|migrate|all]"
        echo ""
        echo "Commands:"
        echo "  build    - Build and push Docker image to ACR"
        echo "  deploy   - Deploy to AKS (without building)"
        echo "  migrate  - Run database migrations"
        echo "  all      - Build, push, and deploy (default)"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Done! 🎉"
echo "=========================================="
