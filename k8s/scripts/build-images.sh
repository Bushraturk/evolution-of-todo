#!/bin/bash

# Build Docker images for Todo Chatbot
# This script builds both backend and frontend images with multi-stage builds

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
BACKEND_DOCKERFILE="k8s/dockerfiles/backend.Dockerfile"
FRONTEND_DOCKERFILE="k8s/dockerfiles/frontend.Dockerfile"
BACKEND_CONTEXT="phase4-chatbot/backend"
FRONTEND_CONTEXT="phase4-chatbot/frontend"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Building Docker Images for Todo Chatbot${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

# Build backend image
echo -e "${YELLOW}Building backend image...${NC}"
echo "Image: ${BACKEND_IMAGE}:${TAG}"
echo "Dockerfile: ${BACKEND_DOCKERFILE}"
echo "Context: ${BACKEND_CONTEXT}"
echo ""

docker build \
    -t "${BACKEND_IMAGE}:${TAG}" \
    -f "${BACKEND_DOCKERFILE}" \
    "${BACKEND_CONTEXT}"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend image built successfully${NC}"
    BACKEND_SIZE=$(docker images "${BACKEND_IMAGE}:${TAG}" --format "{{.Size}}")
    echo "Size: ${BACKEND_SIZE}"
else
    echo -e "${RED}✗ Backend image build failed${NC}"
    exit 1
fi

echo ""

# Build frontend image
echo -e "${YELLOW}Building frontend image...${NC}"
echo "Image: ${FRONTEND_IMAGE}:${TAG}"
echo "Dockerfile: ${FRONTEND_DOCKERFILE}"
echo "Context: ${FRONTEND_CONTEXT}"
echo ""

docker build \
    -t "${FRONTEND_IMAGE}:${TAG}" \
    -f "${FRONTEND_DOCKERFILE}" \
    "${FRONTEND_CONTEXT}"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend image built successfully${NC}"
    FRONTEND_SIZE=$(docker images "${FRONTEND_IMAGE}:${TAG}" --format "{{.Size}}")
    echo "Size: ${FRONTEND_SIZE}"
else
    echo -e "${RED}✗ Frontend image build failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Build Summary${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Backend:  ${BACKEND_IMAGE}:${TAG} (${BACKEND_SIZE})"
echo "Frontend: ${FRONTEND_IMAGE}:${TAG} (${FRONTEND_SIZE})"
echo ""
echo -e "${GREEN}✓ All images built successfully${NC}"
echo ""
echo "Next steps:"
echo "  1. Test images locally: ./k8s/scripts/test-images.sh"
echo "  2. Load to Minikube: ./k8s/scripts/load-images.sh"
echo "  3. Deploy with Helm: helm install todo-chatbot ./k8s/helm-charts/todo-chatbot/"
