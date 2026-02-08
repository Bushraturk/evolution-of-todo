#!/bin/bash

# Load Docker images to Minikube
# This script loads built images into Minikube's Docker environment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKEND_IMAGE="todo-backend"
FRONTEND_IMAGE="todo-frontend"
TAG="${TAG:-latest}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Loading Images to Minikube${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if Minikube is running
if ! minikube status | grep -q "Running"; then
    echo -e "${RED}Error: Minikube is not running${NC}"
    echo "Please start Minikube first: minikube start"
    exit 1
fi

# Check if images exist
if ! docker images "${BACKEND_IMAGE}:${TAG}" --format "{{.Repository}}" | grep -q "${BACKEND_IMAGE}"; then
    echo -e "${RED}Error: Backend image not found${NC}"
    echo "Please build images first: ./k8s/scripts/build-images.sh"
    exit 1
fi

if ! docker images "${FRONTEND_IMAGE}:${TAG}" --format "{{.Repository}}" | grep -q "${FRONTEND_IMAGE}"; then
    echo -e "${RED}Error: Frontend image not found${NC}"
    echo "Please build images first: ./k8s/scripts/build-images.sh"
    exit 1
fi

echo -e "${YELLOW}Loading backend image to Minikube...${NC}"
minikube image load "${BACKEND_IMAGE}:${TAG}"
echo -e "${GREEN}✓ Backend image loaded${NC}"

echo ""

echo -e "${YELLOW}Loading frontend image to Minikube...${NC}"
minikube image load "${FRONTEND_IMAGE}:${TAG}"
echo -e "${GREEN}✓ Frontend image loaded${NC}"

echo ""

echo -e "${YELLOW}Verifying images in Minikube...${NC}"
echo ""

# List images in Minikube
minikube image ls | grep todo || echo "No todo images found"

echo ""
echo -e "${GREEN}✓ Images loaded successfully${NC}"
echo ""
echo "Images are now available in Minikube's Docker environment"
echo ""
echo "Next steps:"
echo "  1. Create secrets: ./k8s/scripts/create-secrets.sh"
echo "  2. Deploy with Helm: helm install todo-chatbot ./k8s/helm-charts/todo-chatbot/"
