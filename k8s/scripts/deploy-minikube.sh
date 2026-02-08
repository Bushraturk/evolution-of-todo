#!/bin/bash

# Deploy Todo Chatbot to Minikube
# This script automates the complete deployment process

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CHART_PATH="k8s/helm-charts/todo-chatbot"
RELEASE_NAME="todo-chatbot"
NAMESPACE="default"
MEMORY="${MEMORY:-4096}"
CPUS="${CPUS:-2}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Todo Chatbot - Minikube Deployment${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Step 1: Check prerequisites
echo -e "${YELLOW}Step 1: Checking prerequisites...${NC}"
echo ""

# Check if Minikube is installed
if ! command -v minikube &> /dev/null; then
    echo -e "${RED}Error: Minikube is not installed${NC}"
    echo "Please install Minikube: https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi
echo -e "${GREEN}✓${NC} Minikube installed"

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    echo "Please install kubectl: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi
echo -e "${GREEN}✓${NC} kubectl installed"

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    echo -e "${RED}Error: Helm is not installed${NC}"
    echo "Please install Helm: https://helm.sh/docs/intro/install/"
    exit 1
fi
echo -e "${GREEN}✓${NC} Helm installed"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    echo "Please start Docker Desktop and try again"
    exit 1
fi
echo -e "${GREEN}✓${NC} Docker running"

echo ""

# Step 2: Start Minikube
echo -e "${YELLOW}Step 2: Starting Minikube...${NC}"
echo ""

if minikube status | grep -q "Running"; then
    echo -e "${GREEN}✓${NC} Minikube is already running"
else
    echo "Starting Minikube with ${MEMORY}MB RAM and ${CPUS} CPUs..."
    minikube start --memory=${MEMORY} --cpus=${CPUS} --driver=docker
    echo -e "${GREEN}✓${NC} Minikube started successfully"
fi

echo ""

# Step 3: Build Docker images
echo -e "${YELLOW}Step 3: Building Docker images...${NC}"
echo ""

./k8s/scripts/build-images.sh

echo ""

# Step 4: Load images to Minikube
echo -e "${YELLOW}Step 4: Loading images to Minikube...${NC}"
echo ""

./k8s/scripts/load-images.sh

echo ""

# Step 5: Create secrets
echo -e "${YELLOW}Step 5: Creating Kubernetes secrets...${NC}"
echo ""

./k8s/scripts/create-secrets.sh

echo ""

# Step 6: Deploy with Helm
echo -e "${YELLOW}Step 6: Deploying with Helm...${NC}"
echo ""

# Check if release already exists
if helm list -n ${NAMESPACE} | grep -q ${RELEASE_NAME}; then
    echo "Release ${RELEASE_NAME} already exists. Upgrading..."
    helm upgrade ${RELEASE_NAME} ${CHART_PATH} -n ${NAMESPACE}
else
    echo "Installing release ${RELEASE_NAME}..."
    helm install ${RELEASE_NAME} ${CHART_PATH} -n ${NAMESPACE}
fi

echo -e "${GREEN}✓${NC} Helm deployment complete"

echo ""

# Step 7: Verify deployment
echo -e "${YELLOW}Step 7: Verifying deployment...${NC}"
echo ""

./k8s/scripts/verify-deployment.sh

echo ""

# Step 8: Access instructions
echo -e "${YELLOW}Step 8: Access application...${NC}"
echo ""

./k8s/scripts/access-application.sh

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete! 🚀${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Your Todo Chatbot is now running on Minikube!"
echo ""
echo "Next steps:"
echo "  1. Start Minikube tunnel: minikube tunnel (in separate terminal)"
echo "  2. Access application: http://localhost"
echo "  3. View logs: kubectl logs -l app.kubernetes.io/name=todo-chatbot"
echo "  4. Scale application: kubectl scale deployment backend --replicas=3"
echo ""
echo "To cleanup:"
echo "  helm uninstall ${RELEASE_NAME}"
echo "  minikube stop"
