#!/bin/bash

# Scale Todo Chatbot deployment replicas
# This script manages horizontal scaling for backend and frontend

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="default"

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -c, --component COMPONENT    Component to scale (backend|frontend|all)"
    echo "  -r, --replicas REPLICAS      Number of replicas (required)"
    echo "  -w, --wait                   Wait for scaling to complete"
    echo "  -a, --autoscale              Enable horizontal pod autoscaling"
    echo "  --min MIN                    Minimum replicas for autoscaling (default: 1)"
    echo "  --max MAX                    Maximum replicas for autoscaling (default: 10)"
    echo "  --cpu CPU                    CPU threshold for autoscaling (default: 70)"
    echo "  -h, --help                   Display this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --component backend --replicas 3"
    echo "  $0 --component all --replicas 2 --wait"
    echo "  $0 -c frontend -r 5 -w"
    echo "  $0 --component backend --autoscale --min 2 --max 10 --cpu 80"
    exit 1
}

# Parse command line arguments
COMPONENT=""
REPLICAS=""
WAIT=false
AUTOSCALE=false
MIN_REPLICAS=1
MAX_REPLICAS=10
CPU_THRESHOLD=70

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--component)
            COMPONENT="$2"
            shift 2
            ;;
        -r|--replicas)
            REPLICAS="$2"
            shift 2
            ;;
        -w|--wait)
            WAIT=true
            shift
            ;;
        -a|--autoscale)
            AUTOSCALE=true
            shift
            ;;
        --min)
            MIN_REPLICAS="$2"
            shift 2
            ;;
        --max)
            MAX_REPLICAS="$2"
            shift 2
            ;;
        --cpu)
            CPU_THRESHOLD="$2"
            shift 2
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
if [ -z "$COMPONENT" ]; then
    echo -e "${RED}Error: Component is required${NC}"
    usage
fi

if [[ "$COMPONENT" != "backend" && "$COMPONENT" != "frontend" && "$COMPONENT" != "all" ]]; then
    echo -e "${RED}Error: Invalid component '$COMPONENT'. Must be 'backend', 'frontend', or 'all'${NC}"
    exit 1
fi

# Validate replicas (required for manual scaling)
if [ "$AUTOSCALE" = false ] && [ -z "$REPLICAS" ]; then
    echo -e "${RED}Error: Replicas count is required for manual scaling${NC}"
    usage
fi

# Validate replicas is a number
if [ -n "$REPLICAS" ] && ! [[ "$REPLICAS" =~ ^[0-9]+$ ]]; then
    echo -e "${RED}Error: Replicas must be a positive integer${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Scale: Todo Chatbot${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Component: $COMPONENT"
if [ "$AUTOSCALE" = true ]; then
    echo "Mode: Autoscaling"
    echo "Min Replicas: $MIN_REPLICAS"
    echo "Max Replicas: $MAX_REPLICAS"
    echo "CPU Threshold: ${CPU_THRESHOLD}%"
else
    echo "Mode: Manual Scaling"
    echo "Target Replicas: $REPLICAS"
fi
echo "Namespace: $NAMESPACE"
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    exit 1
fi

# Function to scale component manually
scale_component() {
    local component=$1
    local replicas=$2

    echo -e "${YELLOW}Scaling ${component} to ${replicas} replicas...${NC}"

    # Show current status
    echo "Current status:"
    kubectl get deployment/${component} -n ${NAMESPACE}
    echo ""

    # Perform scaling
    if kubectl scale deployment/${component} --replicas=${replicas} -n ${NAMESPACE}; then
        echo -e "${GREEN}✓ Scaling initiated for ${component}${NC}"
    else
        echo -e "${RED}✗ Scaling failed for ${component}${NC}"
        return 1
    fi

    # Wait for scaling if requested
    if [ "$WAIT" = true ]; then
        echo -e "${YELLOW}Waiting for ${component} to scale...${NC}"
        if kubectl wait --for=condition=available --timeout=300s deployment/${component} -n ${NAMESPACE}; then
            echo -e "${GREEN}✓ ${component} scaled successfully${NC}"
        else
            echo -e "${RED}✗ ${component} scaling failed or timed out${NC}"
            return 1
        fi
    fi

    echo ""
}

# Function to enable autoscaling
enable_autoscaling() {
    local component=$1
    local min=$2
    local max=$3
    local cpu=$4

    echo -e "${YELLOW}Enabling autoscaling for ${component}...${NC}"

    # Check if HPA already exists
    if kubectl get hpa ${component} -n ${NAMESPACE} &> /dev/null; then
        echo -e "${YELLOW}⚠ HPA already exists for ${component}. Deleting...${NC}"
        kubectl delete hpa ${component} -n ${NAMESPACE}
    fi

    # Create HPA
    if kubectl autoscale deployment ${component} \
        --min=${min} \
        --max=${max} \
        --cpu-percent=${cpu} \
        -n ${NAMESPACE}; then
        echo -e "${GREEN}✓ Autoscaling enabled for ${component}${NC}"
    else
        echo -e "${RED}✗ Failed to enable autoscaling for ${component}${NC}"
        return 1
    fi

    # Show HPA status
    echo ""
    echo "HPA status:"
    kubectl get hpa ${component} -n ${NAMESPACE}
    echo ""
}

# Perform scaling based on mode
if [ "$AUTOSCALE" = true ]; then
    # Enable autoscaling
    if [ "$COMPONENT" = "all" ]; then
        echo -e "${YELLOW}Enabling autoscaling for all components...${NC}"
        echo ""

        if ! enable_autoscaling "backend" "$MIN_REPLICAS" "$MAX_REPLICAS" "$CPU_THRESHOLD"; then
            echo -e "${RED}Backend autoscaling failed. Stopping.${NC}"
            exit 1
        fi

        if ! enable_autoscaling "frontend" "$MIN_REPLICAS" "$MAX_REPLICAS" "$CPU_THRESHOLD"; then
            echo -e "${RED}Frontend autoscaling failed. Stopping.${NC}"
            exit 1
        fi
    else
        if ! enable_autoscaling "$COMPONENT" "$MIN_REPLICAS" "$MAX_REPLICAS" "$CPU_THRESHOLD"; then
            echo -e "${RED}Autoscaling failed.${NC}"
            exit 1
        fi
    fi
else
    # Manual scaling
    if [ "$COMPONENT" = "all" ]; then
        echo -e "${YELLOW}Scaling all components...${NC}"
        echo ""

        if ! scale_component "backend" "$REPLICAS"; then
            echo -e "${RED}Backend scaling failed. Stopping.${NC}"
            exit 1
        fi

        if ! scale_component "frontend" "$REPLICAS"; then
            echo -e "${RED}Frontend scaling failed. Stopping.${NC}"
            exit 1
        fi
    else
        if ! scale_component "$COMPONENT" "$REPLICAS"; then
            echo -e "${RED}Scaling failed.${NC}"
            exit 1
        fi
    fi
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Scaling Summary${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Show deployment status
echo "Current deployment status:"
kubectl get deployments -n ${NAMESPACE} -l app.kubernetes.io/name=todo-chatbot

echo ""
echo "Current pod status:"
kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=todo-chatbot

if [ "$AUTOSCALE" = true ]; then
    echo ""
    echo "HPA status:"
    kubectl get hpa -n ${NAMESPACE}
fi

echo ""
echo -e "${GREEN}✓ Scaling completed${NC}"
echo ""
echo "Next steps:"
echo "  1. Monitor pods: kubectl get pods -n ${NAMESPACE} -w"
echo "  2. Check resource usage: kubectl top pods -n ${NAMESPACE}"
if [ "$AUTOSCALE" = true ]; then
    echo "  3. Monitor HPA: kubectl get hpa -n ${NAMESPACE} -w"
    echo "  4. Disable autoscaling: kubectl delete hpa ${COMPONENT} -n ${NAMESPACE}"
else
    echo "  3. Enable autoscaling: $0 --component ${COMPONENT} --autoscale"
fi
echo "  5. Verify application: ./k8s/scripts/access-application.sh"
echo ""
