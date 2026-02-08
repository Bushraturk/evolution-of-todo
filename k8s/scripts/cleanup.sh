#!/bin/bash

# Cleanup Todo Chatbot deployment from Minikube
# This script removes all deployed resources and optionally cleans up Minikube

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="default"
RELEASE_NAME="todo-chatbot"

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --all                Remove everything including Minikube cluster"
    echo "  --keep-secrets       Keep secrets (useful for redeployment)"
    echo "  --keep-images        Keep Docker images"
    echo "  -h, --help           Display this help message"
    echo ""
    echo "Examples:"
    echo "  $0                   # Remove deployment only"
    echo "  $0 --all             # Remove everything including Minikube"
    echo "  $0 --keep-secrets    # Remove deployment but keep secrets"
    exit 1
}

# Parse command line arguments
REMOVE_ALL=false
KEEP_SECRETS=false
KEEP_IMAGES=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            REMOVE_ALL=true
            shift
            ;;
        --keep-secrets)
            KEEP_SECRETS=true
            shift
            ;;
        --keep-images)
            KEEP_IMAGES=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Cleanup: Todo Chatbot${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Confirm cleanup
echo -e "${YELLOW}⚠ Warning: This will remove the following:${NC}"
echo "  - Helm release: ${RELEASE_NAME}"
echo "  - Kubernetes deployments, services, pods"
if [ "$KEEP_SECRETS" = false ]; then
    echo "  - Kubernetes secrets"
fi
if [ "$KEEP_IMAGES" = false ]; then
    echo "  - Docker images (from Minikube)"
fi
if [ "$REMOVE_ALL" = true ]; then
    echo "  - Minikube cluster (all data will be lost)"
fi
echo ""

read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled"
    exit 0
fi

echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    exit 1
fi

# Check if Helm is available
if ! command -v helm &> /dev/null; then
    echo -e "${RED}Error: Helm is not installed${NC}"
    exit 1
fi

# Step 1: Uninstall Helm release
echo -e "${YELLOW}Step 1: Uninstalling Helm release...${NC}"

if helm list -n ${NAMESPACE} | grep -q ${RELEASE_NAME}; then
    if helm uninstall ${RELEASE_NAME} -n ${NAMESPACE}; then
        echo -e "${GREEN}✓ Helm release uninstalled${NC}"
    else
        echo -e "${RED}✗ Failed to uninstall Helm release${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Helm release not found${NC}"
fi

echo ""

# Step 2: Delete secrets (if not keeping)
if [ "$KEEP_SECRETS" = false ]; then
    echo -e "${YELLOW}Step 2: Deleting secrets...${NC}"

    if kubectl get secret todo-secrets -n ${NAMESPACE} &> /dev/null; then
        if kubectl delete secret todo-secrets -n ${NAMESPACE}; then
            echo -e "${GREEN}✓ Secrets deleted${NC}"
        else
            echo -e "${RED}✗ Failed to delete secrets${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Secrets not found${NC}"
    fi
else
    echo -e "${YELLOW}Step 2: Keeping secrets (--keep-secrets specified)${NC}"
fi

echo ""

# Step 3: Delete any remaining resources
echo -e "${YELLOW}Step 3: Cleaning up remaining resources...${NC}"

# Delete deployments
if kubectl get deployments -n ${NAMESPACE} -l app.kubernetes.io/name=todo-chatbot &> /dev/null; then
    kubectl delete deployments -n ${NAMESPACE} -l app.kubernetes.io/name=todo-chatbot
    echo -e "${GREEN}✓ Deployments deleted${NC}"
fi

# Delete services
if kubectl get services -n ${NAMESPACE} -l app.kubernetes.io/name=todo-chatbot &> /dev/null; then
    kubectl delete services -n ${NAMESPACE} -l app.kubernetes.io/name=todo-chatbot
    echo -e "${GREEN}✓ Services deleted${NC}"
fi

# Delete configmaps
if kubectl get configmaps -n ${NAMESPACE} -l app.kubernetes.io/name=todo-chatbot &> /dev/null; then
    kubectl delete configmaps -n ${NAMESPACE} -l app.kubernetes.io/name=todo-chatbot
    echo -e "${GREEN}✓ ConfigMaps deleted${NC}"
fi

# Delete HPAs
if kubectl get hpa -n ${NAMESPACE} &> /dev/null; then
    kubectl delete hpa --all -n ${NAMESPACE} 2>/dev/null || true
    echo -e "${GREEN}✓ HPAs deleted${NC}"
fi

echo ""

# Step 4: Remove images from Minikube (if not keeping)
if [ "$KEEP_IMAGES" = false ]; then
    echo -e "${YELLOW}Step 4: Removing images from Minikube...${NC}"

    if command -v minikube &> /dev/null; then
        if minikube status &> /dev/null; then
            minikube image rm todo-backend:latest 2>/dev/null || true
            minikube image rm todo-frontend:latest 2>/dev/null || true
            echo -e "${GREEN}✓ Images removed from Minikube${NC}"
        else
            echo -e "${YELLOW}⚠ Minikube not running${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Minikube not installed${NC}"
    fi
else
    echo -e "${YELLOW}Step 4: Keeping images (--keep-images specified)${NC}"
fi

echo ""

# Step 5: Remove Minikube cluster (if --all specified)
if [ "$REMOVE_ALL" = true ]; then
    echo -e "${YELLOW}Step 5: Removing Minikube cluster...${NC}"

    if command -v minikube &> /dev/null; then
        if minikube delete; then
            echo -e "${GREEN}✓ Minikube cluster deleted${NC}"
        else
            echo -e "${RED}✗ Failed to delete Minikube cluster${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Minikube not installed${NC}"
    fi
else
    echo -e "${YELLOW}Step 5: Keeping Minikube cluster (use --all to remove)${NC}"
fi

echo ""

# Verify cleanup
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Cleanup Verification${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ "$REMOVE_ALL" = false ]; then
    echo "Remaining resources in namespace ${NAMESPACE}:"
    kubectl get all -n ${NAMESPACE} -l app.kubernetes.io/name=todo-chatbot 2>/dev/null || echo "  (none)"

    if [ "$KEEP_SECRETS" = true ]; then
        echo ""
        echo "Secrets (kept):"
        kubectl get secrets -n ${NAMESPACE} | grep todo || echo "  (none)"
    fi

    echo ""
    echo "Minikube status:"
    minikube status 2>/dev/null || echo "  (not running)"
else
    echo "Minikube cluster removed"
    echo "All resources cleaned up"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Cleanup Complete${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

if [ "$REMOVE_ALL" = false ]; then
    echo "Next steps:"
    echo "  1. To redeploy: ./k8s/scripts/deploy-minikube.sh"
    if [ "$KEEP_SECRETS" = true ]; then
        echo "  2. Secrets are preserved for redeployment"
    else
        echo "  2. Recreate secrets: ./k8s/scripts/create-secrets.sh"
    fi
    echo "  3. To remove Minikube: $0 --all"
else
    echo "To start fresh:"
    echo "  1. Start Minikube: minikube start --memory=4096 --cpus=2"
    echo "  2. Deploy application: ./k8s/scripts/deploy-minikube.sh"
fi

echo ""
