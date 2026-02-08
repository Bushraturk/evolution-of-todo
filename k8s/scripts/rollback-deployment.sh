#!/bin/bash

# Rollback Todo Chatbot deployment to previous version
# This script performs rollback for backend and frontend deployments

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
    echo "  -c, --component COMPONENT    Component to rollback (backend|frontend|all)"
    echo "  -r, --revision REVISION      Revision number to rollback to (default: previous)"
    echo "  -w, --wait                   Wait for rollback to complete"
    echo "  -h, --help                   Display this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --component backend"
    echo "  $0 --component all --wait"
    echo "  $0 -c frontend -r 2 -w"
    echo "  $0 --component backend --revision 1"
    exit 1
}

# Parse command line arguments
COMPONENT="all"
REVISION=""
WAIT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--component)
            COMPONENT="$2"
            shift 2
            ;;
        -r|--revision)
            REVISION="$2"
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
echo -e "${BLUE}Rollback: Todo Chatbot${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Component: $COMPONENT"
if [ -n "$REVISION" ]; then
    echo "Target Revision: $REVISION"
else
    echo "Target Revision: Previous"
fi
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
    exit 1
fi

# Function to show rollout history
show_history() {
    local component=$1

    echo -e "${YELLOW}Rollout history for ${component}:${NC}"
    kubectl rollout history deployment/${component} -n ${NAMESPACE}
    echo ""
}

# Function to rollback component
rollback_component() {
    local component=$1
    local revision=$2

    echo -e "${YELLOW}Rolling back ${component}...${NC}"

    # Show current status
    echo "Current status:"
    kubectl get deployment/${component} -n ${NAMESPACE}
    echo ""

    # Perform rollback
    if [ -n "$revision" ]; then
        echo "Rolling back to revision ${revision}..."
        if kubectl rollout undo deployment/${component} -n ${NAMESPACE} --to-revision=${revision}; then
            echo -e "${GREEN}✓ Rollback initiated for ${component} to revision ${revision}${NC}"
        else
            echo -e "${RED}✗ Rollback failed for ${component}${NC}"
            return 1
        fi
    else
        echo "Rolling back to previous revision..."
        if kubectl rollout undo deployment/${component} -n ${NAMESPACE}; then
            echo -e "${GREEN}✓ Rollback initiated for ${component}${NC}"
        else
            echo -e "${RED}✗ Rollback failed for ${component}${NC}"
            return 1
        fi
    fi

    # Wait for rollback if requested
    if [ "$WAIT" = true ]; then
        echo -e "${YELLOW}Waiting for ${component} rollback to complete...${NC}"
        if kubectl rollout status deployment/${component} -n ${NAMESPACE} --timeout=300s; then
            echo -e "${GREEN}✓ ${component} rollback completed successfully${NC}"
        else
            echo -e "${RED}✗ ${component} rollback failed or timed out${NC}"
            return 1
        fi
    fi

    echo ""
}

# Show Helm release history
echo -e "${YELLOW}Helm release history:${NC}"
helm history ${RELEASE_NAME} -n ${NAMESPACE}
echo ""

# Perform rollback based on component
if [ "$COMPONENT" = "all" ]; then
    echo -e "${YELLOW}Rolling back all components...${NC}"
    echo ""

    # Show history for both components
    show_history "backend"
    show_history "frontend"

    # Confirm rollback
    echo -e "${YELLOW}⚠ Warning: This will rollback both backend and frontend deployments${NC}"
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Rollback cancelled"
        exit 0
    fi

    # Rollback backend
    if ! rollback_component "backend" "$REVISION"; then
        echo -e "${RED}Backend rollback failed. Stopping.${NC}"
        exit 1
    fi

    # Rollback frontend
    if ! rollback_component "frontend" "$REVISION"; then
        echo -e "${RED}Frontend rollback failed. Stopping.${NC}"
        exit 1
    fi
else
    # Show history for single component
    show_history "$COMPONENT"

    # Confirm rollback
    echo -e "${YELLOW}⚠ Warning: This will rollback the ${COMPONENT} deployment${NC}"
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Rollback cancelled"
        exit 0
    fi

    # Rollback single component
    if ! rollback_component "$COMPONENT" "$REVISION"; then
        echo -e "${RED}Rollback failed.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Rollback Summary${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Show deployment status
echo "Current deployment status:"
kubectl get deployments -n ${NAMESPACE} -l app.kubernetes.io/name=todo-chatbot

echo ""
echo "Current pod status:"
kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=todo-chatbot

echo ""
echo -e "${GREEN}✓ Rollback completed${NC}"
echo ""
echo "Next steps:"
echo "  1. Verify application: ./k8s/scripts/access-application.sh"
echo "  2. Check logs: kubectl logs -l app.kubernetes.io/component=${COMPONENT} -n ${NAMESPACE}"
echo "  3. Monitor pods: kubectl get pods -n ${NAMESPACE} -w"
echo "  4. View history: kubectl rollout history deployment/${COMPONENT} -n ${NAMESPACE}"
echo ""
