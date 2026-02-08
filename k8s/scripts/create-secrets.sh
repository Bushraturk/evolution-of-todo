#!/bin/bash

# Create Kubernetes secrets for Todo Chatbot
# This script creates secrets from environment variables or .env file

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SECRET_NAME="todo-secrets"
NAMESPACE="default"
ENV_FILE="k8s/.env"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Creating Kubernetes Secrets${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    exit 1
fi

# Check if secret already exists
if kubectl get secret ${SECRET_NAME} -n ${NAMESPACE} &> /dev/null; then
    echo -e "${YELLOW}Secret ${SECRET_NAME} already exists${NC}"
    read -p "Do you want to delete and recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl delete secret ${SECRET_NAME} -n ${NAMESPACE}
        echo -e "${GREEN}✓ Existing secret deleted${NC}"
    else
        echo "Keeping existing secret"
        exit 0
    fi
fi

echo ""

# Check if .env file exists
if [ -f "${ENV_FILE}" ]; then
    echo -e "${YELLOW}Creating secret from ${ENV_FILE}...${NC}"
    kubectl create secret generic ${SECRET_NAME} \
        --from-env-file=${ENV_FILE} \
        -n ${NAMESPACE}
    echo -e "${GREEN}✓ Secret created from ${ENV_FILE}${NC}"
else
    echo -e "${YELLOW}No ${ENV_FILE} found. Creating secret from environment variables...${NC}"
    echo ""

    # Prompt for required values
    echo "Please provide the following values:"
    echo ""

    read -p "DATABASE_URL: " DATABASE_URL
    read -p "GROQ_API_KEY: " GROQ_API_KEY
    read -p "JWT_SECRET: " JWT_SECRET

    # Use defaults for optional values
    GROQ_BASE_URL="${GROQ_BASE_URL:-https://api.groq.com/openai/v1}"
    GROQ_MODEL="${GROQ_MODEL:-llama-3.3-70b-versatile}"

    echo ""
    echo -e "${YELLOW}Creating secret...${NC}"

    kubectl create secret generic ${SECRET_NAME} \
        --from-literal=DATABASE_URL="${DATABASE_URL}" \
        --from-literal=GROQ_API_KEY="${GROQ_API_KEY}" \
        --from-literal=JWT_SECRET="${JWT_SECRET}" \
        --from-literal=GROQ_BASE_URL="${GROQ_BASE_URL}" \
        --from-literal=GROQ_MODEL="${GROQ_MODEL}" \
        -n ${NAMESPACE}

    echo -e "${GREEN}✓ Secret created from environment variables${NC}"
fi

echo ""

# Verify secret was created
echo -e "${YELLOW}Verifying secret...${NC}"
kubectl get secret ${SECRET_NAME} -n ${NAMESPACE}

echo ""
echo -e "${GREEN}✓ Secret ${SECRET_NAME} created successfully${NC}"
echo ""
echo "Secret contains:"
echo "  - DATABASE_URL"
echo "  - GROQ_API_KEY"
echo "  - JWT_SECRET"
echo "  - GROQ_BASE_URL"
echo "  - GROQ_MODEL"
echo ""
echo "Next steps:"
echo "  1. Deploy with Helm: helm install todo-chatbot ./k8s/helm-charts/todo-chatbot/"
echo "  2. Verify deployment: ./k8s/scripts/verify-deployment.sh"
