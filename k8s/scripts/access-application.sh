#!/bin/bash

# Access Todo Chatbot application on Minikube
# This script provides instructions for accessing the deployed application

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="default"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Accessing Todo Chatbot${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    exit 1
fi

# Get service type
SERVICE_TYPE=$(kubectl get service frontend -n ${NAMESPACE} -o jsonpath='{.spec.type}')

echo "Frontend service type: ${SERVICE_TYPE}"
echo ""

if [ "$SERVICE_TYPE" = "LoadBalancer" ]; then
    echo -e "${YELLOW}Option 1: Using Minikube Tunnel (Recommended)${NC}"
    echo ""
    echo "1. Start Minikube tunnel in a separate terminal:"
    echo "   ${GREEN}minikube tunnel${NC}"
    echo ""
    echo "2. Get the external IP:"
    echo "   ${GREEN}kubectl get service frontend -n ${NAMESPACE}${NC}"
    echo ""
    echo "3. Access the application:"
    echo "   ${GREEN}http://localhost${NC} or ${GREEN}http://127.0.0.1${NC}"
    echo ""
    echo -e "${YELLOW}Option 2: Using NodePort${NC}"
    echo ""
    NODE_PORT=$(kubectl get service frontend -n ${NAMESPACE} -o jsonpath='{.spec.ports[0].nodePort}')
    MINIKUBE_IP=$(minikube ip)
    echo "Access URL: ${GREEN}http://${MINIKUBE_IP}:${NODE_PORT}${NC}"
    echo ""
    echo -e "${YELLOW}Option 3: Using Port Forwarding${NC}"
    echo ""
    echo "1. Forward local port to frontend service:"
    echo "   ${GREEN}kubectl port-forward service/frontend 3000:80 -n ${NAMESPACE}${NC}"
    echo ""
    echo "2. Access the application:"
    echo "   ${GREEN}http://localhost:3000${NC}"
    echo ""
elif [ "$SERVICE_TYPE" = "NodePort" ]; then
    echo -e "${YELLOW}Using NodePort${NC}"
    echo ""
    NODE_PORT=$(kubectl get service frontend -n ${NAMESPACE} -o jsonpath='{.spec.ports[0].nodePort}')
    MINIKUBE_IP=$(minikube ip)
    echo "Access URL: ${GREEN}http://${MINIKUBE_IP}:${NODE_PORT}${NC}"
    echo ""
else
    echo -e "${YELLOW}Using Port Forwarding${NC}"
    echo ""
    echo "1. Forward local port to frontend service:"
    echo "   ${GREEN}kubectl port-forward service/frontend 3000:80 -n ${NAMESPACE}${NC}"
    echo ""
    echo "2. Access the application:"
    echo "   ${GREEN}http://localhost:3000${NC}"
    echo ""
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Additional Commands${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "View backend logs:"
echo "  ${GREEN}kubectl logs -l app.kubernetes.io/component=backend -n ${NAMESPACE}${NC}"
echo ""
echo "View frontend logs:"
echo "  ${GREEN}kubectl logs -l app.kubernetes.io/component=frontend -n ${NAMESPACE}${NC}"
echo ""
echo "Scale backend:"
echo "  ${GREEN}kubectl scale deployment backend --replicas=3 -n ${NAMESPACE}${NC}"
echo ""
echo "Check pod status:"
echo "  ${GREEN}kubectl get pods -n ${NAMESPACE}${NC}"
echo ""
echo "Access backend API directly:"
echo "  ${GREEN}kubectl port-forward service/backend 8000:8000 -n ${NAMESPACE}${NC}"
echo "  Then visit: ${GREEN}http://localhost:8000/docs${NC}"
echo ""
