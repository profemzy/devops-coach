#!/bin/bash
set -e

# Registry URL
REGISTRY="prodacrva1ng1.azurecr.io"
IMAGE_NAME="devops-coach"
TAG="latest"
FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${TAG}"

echo "Building Docker image ${FULL_IMAGE_NAME}..."
# Build targeting the 'app' stage (final stage) for AMD64
docker build --platform linux/amd64 --target app -t "${FULL_IMAGE_NAME}" .

echo "Pushing Docker image ${FULL_IMAGE_NAME}..."
docker push "${FULL_IMAGE_NAME}"

echo "Done! Image pushed to ${FULL_IMAGE_NAME}"
