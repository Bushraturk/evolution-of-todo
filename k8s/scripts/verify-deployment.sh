#!/bin/bash

# Verify Todo Chatbot deployment on Minikube
# This script checks pod status, logs, and health endpoints

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="default"
TIMEOUT=180  # 3 minutes

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Verifying Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    exit 1
fi

# Step 1: Check pod status
echo -e "${YELLOW}Step 1: Checking pod status...${NC}"
echo ""

kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=todo-chatbot

echo ""

# Wait for pods to be ready
echo -e "${YELLOW}Waiting for pods to be ready (timeout: ${TIMEOUT}s)...${NC}"
echo ""

if kubectl wait --for=condition=ready pod \
    -l app.kubernetes.io/name=todo-chatbot \
    -n ${NAMESPACE} \
    --timeout=${TIMEOUT}s; then
    echo -e "${GREEN}✓ All pods are ready${NC}"
else
    echo -e "${RED}✗ Pods failed to become ready${NC}"
    echo ""
    echo "Pod status:"
    kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=todo-chatbot
    echo ""
    echo "Pod events:"
    kubectl get events -n ${NAMESPACE} --sort-by='.lastTimestamp'
    exit 1
fi

echo ""

# Step 2: Check services
echo -e "${YELLOW}Step 2: Checking services...${NC}"
echo ""

kubectl get services -n ${NAMESPACE} -l app.kubernetes.io/name=todo-chatbot

echo ""

# Step 3: Check backend logs
echo -e "${YELLOW}Step 3: Checking backend logs...${NC}"
echo ""

BACKEND_POD=$(kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}')

if [ -n "$BACKEND_POD" ]; then
    echo "Backend pod: $BACKEND_POD"
    echo "Last 10 lines of logs:"
    kubectl logs ${BACKEND_POD} -n ${NAMESPACE} --tail=10
    echo -e "${GREEN}✓ Backend logs accessible${NC}"
else
    echo -e "${RED}✗ Backend pod not found${NC}"
fi

echo ""

# Step 4: Check frontend logs
echo -e "${YELLOW}Step 4: Checking frontend logs...${NC}"
echo ""

FRONTEND_POD=$(kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/component=frontend -o jsonpath='{.items[0].metadata.name}')

if [ -n "$FRONTEND_POD" ]; then
    echo "Frontend pod: $FRONTEND_POD"
    echo "Last 10 lines of logs:"
    kubectl logs ${FRONTEND_POD} -n ${NAMESPACE} --tail=10
    echo -e "${GREEN}✓ Frontend logs accessible${NC}"
else
    echo -e "${RED}✗ Frontend pod not found${NC}"
fi

echo ""

# Step 5: Test health endpoints
echo -e "${YELLOW}Step 5: Testing health endpoints...${NC}"
echo ""

# Test backend health
echo "Testing backend health endpoint..."
if kubectl exec ${BACKEND_POD} -n ${NAMESPACE} -- curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend health check passed${NC}"
else
    echo -e "${YELLOW}⚠ Backend health check failed (may need database connection)${NC}"
fi

# Test frontend health
echo "Testing frontend health endpoint..."
if kubectl exec ${FRONTEND_POD} -n ${NAMESPACE} -- curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend health check passed${NC}"
else
    echo -e "${YELLOW}⚠ Frontend health check failed${NC}"
fi

echo ""

# Step 6: Check resource usage
echo -e "${YELLOW}Step 6: Checking resource usage...${NC}"
echo ""

if kubectl top pods -n ${NAMESPACE} -l app.kubernetes.io/name=todo-chatbot 2>/dev/null; then
    echo -e "${GREEN}✓ Resource metrics available${NC}"
else
    echo -e "${YELLOW}⚠ Metrics server not available (install with: minikube addons enable metrics-server)${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Verification Summary${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${GREEN}✓ Deployment verification complete${NC}"
echo ""
echo "Deployment status:"
kubectl get all -n ${NAMESPACE} -l app.kubernetes.io/name=todo-chatbot
echo ""
echo "Next steps:"
echo "  1. Access application: ./k8s/scripts/access-application.sh"
echo "  2. View logs: kubectl logs -f ${BACKEND_POD}"
echo "  3. Scale application: kubectl scale deployment backend --replicas=3"
