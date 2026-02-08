#!/bin/bash

# Test rolling update with zero downtime verification
# This script performs a rolling update and verifies zero downtime

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="default"
COMPONENT="backend"
TEST_DURATION=60  # seconds
REQUEST_INTERVAL=1  # seconds between requests

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -c, --component COMPONENT    Component to test (backend|frontend) (default: backend)"
    echo "  -t, --tag TAG                New image tag to deploy (default: latest)"
    echo "  -d, --duration DURATION      Test duration in seconds (default: 60)"
    echo "  -i, --interval INTERVAL      Request interval in seconds (default: 1)"
    echo "  -h, --help                   Display this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --component backend --tag v1.0.1"
    echo "  $0 -c frontend -t latest -d 120"
    exit 1
}

# Parse command line arguments
TAG="latest"

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
        -d|--duration)
            TEST_DURATION="$2"
            shift 2
            ;;
        -i|--interval)
            REQUEST_INTERVAL="$2"
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
if [[ "$COMPONENT" != "backend" && "$COMPONENT" != "frontend" ]]; then
    echo -e "${RED}Error: Invalid component '$COMPONENT'. Must be 'backend' or 'frontend'${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Rolling Update: Zero Downtime${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Component: $COMPONENT"
echo "New Tag: $TAG"
echo "Test Duration: ${TEST_DURATION}s"
echo "Request Interval: ${REQUEST_INTERVAL}s"
echo "Namespace: $NAMESPACE"
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    exit 1
fi

# Check if curl is available
if ! command -v curl &> /dev/null; then
    echo -e "${RED}Error: curl is not installed${NC}"
    exit 1
fi

# Determine service URL
if [ "$COMPONENT" = "backend" ]; then
    SERVICE_NAME="backend"
    SERVICE_PORT=8000
    HEALTH_PATH="/health"
else
    SERVICE_NAME="frontend"
    SERVICE_PORT=80
    HEALTH_PATH="/api/health"
fi

# Get service endpoint
echo -e "${YELLOW}Getting service endpoint...${NC}"

# Try to get LoadBalancer external IP
EXTERNAL_IP=$(kubectl get service ${SERVICE_NAME} -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")

if [ -z "$EXTERNAL_IP" ]; then
    # Try NodePort
    NODE_PORT=$(kubectl get service ${SERVICE_NAME} -n ${NAMESPACE} -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null || echo "")
    if [ -n "$NODE_PORT" ]; then
        MINIKUBE_IP=$(minikube ip 2>/dev/null || echo "127.0.0.1")
        SERVICE_URL="http://${MINIKUBE_IP}:${NODE_PORT}${HEALTH_PATH}"
    else
        # Use port-forward
        echo -e "${YELLOW}Using port-forward for testing...${NC}"
        kubectl port-forward service/${SERVICE_NAME} ${SERVICE_PORT}:${SERVICE_PORT} -n ${NAMESPACE} &
        PORT_FORWARD_PID=$!
        sleep 3
        SERVICE_URL="http://localhost:${SERVICE_PORT}${HEALTH_PATH}"
    fi
else
    SERVICE_URL="http://${EXTERNAL_IP}:${SERVICE_PORT}${HEALTH_PATH}"
fi

echo "Service URL: $SERVICE_URL"
echo ""

# Test initial connectivity
echo -e "${YELLOW}Testing initial connectivity...${NC}"
if curl -f -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" | grep -q "200"; then
    echo -e "${GREEN}✓ Service is reachable${NC}"
else
    echo -e "${RED}✗ Service is not reachable. Cannot proceed with test.${NC}"
    [ -n "$PORT_FORWARD_PID" ] && kill $PORT_FORWARD_PID 2>/dev/null
    exit 1
fi
echo ""

# Create temporary files for results
RESULTS_FILE=$(mktemp)
ERRORS_FILE=$(mktemp)

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Cleaning up...${NC}"
    [ -n "$PORT_FORWARD_PID" ] && kill $PORT_FORWARD_PID 2>/dev/null
    [ -n "$MONITOR_PID" ] && kill $MONITOR_PID 2>/dev/null
    rm -f "$RESULTS_FILE" "$ERRORS_FILE"
}

trap cleanup EXIT

# Function to monitor requests
monitor_requests() {
    local start_time=$(date +%s)
    local end_time=$((start_time + TEST_DURATION))
    local total_requests=0
    local successful_requests=0
    local failed_requests=0

    echo "0" > "$RESULTS_FILE"
    echo "0" > "$ERRORS_FILE"

    while [ $(date +%s) -lt $end_time ]; do
        total_requests=$((total_requests + 1))

        # Make request
        if curl -f -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" 2>/dev/null | grep -q "200"; then
            successful_requests=$((successful_requests + 1))
        else
            failed_requests=$((failed_requests + 1))
            echo "$(date +%s)" >> "$ERRORS_FILE"
        fi

        # Update results
        echo "$total_requests $successful_requests $failed_requests" > "$RESULTS_FILE"

        sleep $REQUEST_INTERVAL
    done
}

# Start monitoring in background
echo -e "${YELLOW}Starting request monitoring...${NC}"
monitor_requests &
MONITOR_PID=$!

# Wait a few seconds for monitoring to start
sleep 3

# Show current deployment status
echo ""
echo -e "${YELLOW}Current deployment status:${NC}"
kubectl get deployment/${COMPONENT} -n ${NAMESPACE}
echo ""

# Perform rolling update
echo -e "${YELLOW}Initiating rolling update...${NC}"
echo "Updating ${COMPONENT} to tag ${TAG}..."
echo ""

# Trigger update
kubectl set image deployment/${COMPONENT} ${COMPONENT}=todo-${COMPONENT}:${TAG} -n ${NAMESPACE}

# Monitor rollout status
echo -e "${YELLOW}Monitoring rollout...${NC}"
kubectl rollout status deployment/${COMPONENT} -n ${NAMESPACE} --timeout=300s

echo ""
echo -e "${GREEN}✓ Rollout completed${NC}"
echo ""

# Wait for monitoring to complete
echo -e "${YELLOW}Waiting for test to complete...${NC}"
wait $MONITOR_PID

# Analyze results
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Results${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Read results
if [ -f "$RESULTS_FILE" ]; then
    read total successful failed < "$RESULTS_FILE"

    echo "Total Requests: $total"
    echo "Successful Requests: $successful"
    echo "Failed Requests: $failed"

    if [ $total -gt 0 ]; then
        success_rate=$(awk "BEGIN {printf \"%.2f\", ($successful / $total) * 100}")
        echo "Success Rate: ${success_rate}%"
    fi

    echo ""

    # Determine if zero downtime was achieved
    if [ $failed -eq 0 ]; then
        echo -e "${GREEN}✓ ZERO DOWNTIME ACHIEVED${NC}"
        echo -e "${GREEN}All requests succeeded during rolling update${NC}"
        exit_code=0
    else
        echo -e "${YELLOW}⚠ DOWNTIME DETECTED${NC}"
        echo -e "${YELLOW}$failed requests failed during rolling update${NC}"

        # Show error timestamps
        if [ -f "$ERRORS_FILE" ] && [ -s "$ERRORS_FILE" ]; then
            echo ""
            echo "Failed request timestamps:"
            cat "$ERRORS_FILE"
        fi
        exit_code=1
    fi
else
    echo -e "${RED}✗ Could not read test results${NC}"
    exit_code=1
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Deployment Status${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Show final deployment status
kubectl get deployment/${COMPONENT} -n ${NAMESPACE}

echo ""
echo "Pod status:"
kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/component=${COMPONENT}

echo ""
echo "Rollout history:"
kubectl rollout history deployment/${COMPONENT} -n ${NAMESPACE}

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Recommendations${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ $exit_code -eq 0 ]; then
    echo "✓ Rolling update strategy is working correctly"
    echo "✓ Zero downtime achieved with current configuration"
    echo ""
    echo "Current configuration:"
    kubectl get deployment/${COMPONENT} -n ${NAMESPACE} -o jsonpath='{.spec.strategy}' | jq '.'
else
    echo "⚠ Consider adjusting rolling update strategy:"
    echo "  1. Increase maxSurge to allow more new pods during update"
    echo "  2. Decrease maxUnavailable to keep more old pods running"
    echo "  3. Increase readiness probe initialDelaySeconds"
    echo "  4. Add preStop hook for graceful shutdown"
    echo ""
    echo "Example configuration:"
    echo "  strategy:"
    echo "    type: RollingUpdate"
    echo "    rollingUpdate:"
    echo "      maxSurge: 1"
    echo "      maxUnavailable: 0"
fi

echo ""
exit $exit_code
