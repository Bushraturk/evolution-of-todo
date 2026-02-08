#!/bin/bash

# Update Todo Chatbot deployment with rolling update
# This script performs zero-downtime rolling updates for backend and frontend

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
CHART_PATH="k8s/helm-charts/todo-chatbot"

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -c, --component COMPONENT    Component to update (backend|frontend|all)"
    echo "  -t, --tag TAG                Image tag to deploy (default: latest)"
    echo "  -w, --wait                   Wait for rollout to complete"
    echo "  -h, --help                   Display this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --component backend --tag v1.0.1"
    echo "  $0 --component all --tag v1.0.1 --wait"
    echo "  $0 -c frontend -t latest -w"
    exit 1
}

# Parse command line arguments
COMPONENT="all"
TAG="latest"
WAIT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--component)
            COMPONENT="$2"
            shift 2
            ;;
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -w|--wait)
            WAIT=true
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

# Validate component
if [[ "$COMPONENT" != "backend" && "$COMPONENT" != "frontend" && "$COMPONENT" != "all" ]]; then
    echo -e "${RED}Error: Invalid component '$COMPONENT'. Must be 'backend', 'frontend', or 'all'${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Rolling Update: Todo Chatbot${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Component: $COMPONENT"
echo "Image Tag: $TAG"
echo "Namespace: $NAMESPACE"
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

# Check if release exists
if ! helm list -n ${NAMESPACE} | grep -q ${RELEASE_NAME}; then
    echo -e "${RED}Error: Helm release '${RELEASE_NAME}' not found in namespace '${NAMESPACE}'${NC}"
    echo "Deploy first with: helm install ${RELEASE_NAME} ${CHART_PATH}"
    exit 1
fi

# Function to update component
update_component() {
    local component=$1
    local image_tag=$2

    echo -e "${YELLOW}Updating ${component} to tag ${image_tag}...${NC}"

    # Perform Helm upgrade
    if helm upgrade ${RELEASE_NAME} ${CHART_PATH} \
        --set ${component}.image.tag=${image_tag} \
        --namespace ${NAMESPACE} \
        --reuse-values; then
        echo -e "${GREEN}✓ Helm upgrade successful for ${component}${NC}"
    else
        echo -e "${RED}✗ Helm upgrade failed for ${component}${NC}"
        return 1
    fi

    # Wait for rollout if requested
    if [ "$WAIT" = true ]; then
        echo -e "${YELLOW}Waiting for ${component} rollout to complete...${NC}"
        if kubectl rollout status deployment/${component} -n ${NAMESPACE} --timeout=300s; then
            echo -e "${GREEN}✓ ${component} rollout completed successfully${NC}"
        else
            echo -e "${RED}✗ ${component} rollout failed or timed out${NC}"
            return 1
        fi
    fi

    echo ""
}

# Perform update based on component
if [ "$COMPONENT" = "all" ]; then
    echo -e "${YELLOW}Updating all components...${NC}"
    echo ""

    # Update backend
    if ! update_component "backend" "$TAG"; then
        echo -e "${RED}Backend update failed. Stopping.${NC}"
        exit 1
    fi

    # Update frontend
    if ! update_component "frontend" "$TAG"; then
        echo -e "${RED}Frontend update failed. Stopping.${NC}"
        exit 1
    fi
else
    # Update single component
    if ! update_component "$COMPONENT" "$TAG"; then
        echo -e "${RED}Update failed.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Update Summary${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Show deployment status
echo "Current deployment status:"
kubectl get deployments -n ${NAMESPACE} -l app.kubernetes.io/name=todo-chatbot

echo ""
echo "Current pod status:"
kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=todo-chatbot

echo ""
echo -e "${GREEN}✓ Rolling update completed${NC}"
echo ""
echo "Next steps:"
echo "  1. Verify application: ./k8s/scripts/access-application.sh"
echo "  2. Check logs: kubectl logs -l app.kubernetes.io/component=${COMPONENT} -n ${NAMESPACE}"
echo "  3. Monitor pods: kubectl get pods -n ${NAMESPACE} -w"
echo "  4. Rollback if needed: ./k8s/scripts/rollback-deployment.sh"
echo ""
