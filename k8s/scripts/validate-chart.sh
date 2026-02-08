#!/bin/bash

# Validate Helm chart for Todo Chatbot
# This script runs helm lint and helm template to validate the chart

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
CHART_PATH="k8s/helm-charts/todo-chatbot"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Validating Helm Chart${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    echo -e "${RED}Error: Helm is not installed${NC}"
    echo "Please install Helm: https://helm.sh/docs/intro/install/"
    exit 1
fi

# Check if chart directory exists
if [ ! -d "$CHART_PATH" ]; then
    echo -e "${RED}Error: Chart directory not found: $CHART_PATH${NC}"
    exit 1
fi

echo -e "${YELLOW}Running helm lint...${NC}"
echo ""

# Run helm lint
if helm lint "$CHART_PATH"; then
    echo ""
    echo -e "${GREEN}✓ Helm lint passed${NC}"
else
    echo ""
    echo -e "${RED}✗ Helm lint failed${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Running helm template (dry-run)...${NC}"
echo ""

# Run helm template to validate manifests
if helm template todo-chatbot "$CHART_PATH" > /dev/null; then
    echo -e "${GREEN}✓ Helm template rendered successfully${NC}"
else
    echo -e "${RED}✗ Helm template failed${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Checking for required templates...${NC}"
echo ""

# Check for required template files
REQUIRED_TEMPLATES=(
    "backend-deployment.yaml"
    "backend-service.yaml"
    "frontend-deployment.yaml"
    "frontend-service.yaml"
    "configmap.yaml"
    "secrets.yaml"
    "_helpers.tpl"
    "NOTES.txt"
)

MISSING_TEMPLATES=()

for template in "${REQUIRED_TEMPLATES[@]}"; do
    if [ -f "$CHART_PATH/templates/$template" ]; then
        echo -e "${GREEN}✓${NC} $template"
    else
        echo -e "${RED}✗${NC} $template (missing)"
        MISSING_TEMPLATES+=("$template")
    fi
done

if [ ${#MISSING_TEMPLATES[@]} -gt 0 ]; then
    echo ""
    echo -e "${RED}Error: Missing required templates${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Checking for required values...${NC}"
echo ""

# Check for required value files
REQUIRED_VALUES=(
    "values.yaml"
    "values-dev.yaml"
    "values-prod.yaml"
)

MISSING_VALUES=()

for values_file in "${REQUIRED_VALUES[@]}"; do
    if [ -f "$CHART_PATH/$values_file" ]; then
        echo -e "${GREEN}✓${NC} $values_file"
    else
        echo -e "${RED}✗${NC} $values_file (missing)"
        MISSING_VALUES+=("$values_file")
    fi
done

if [ ${#MISSING_VALUES[@]} -gt 0 ]; then
    echo ""
    echo -e "${RED}Error: Missing required values files${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Validating Chart.yaml...${NC}"
echo ""

# Check Chart.yaml exists and has required fields
if [ ! -f "$CHART_PATH/Chart.yaml" ]; then
    echo -e "${RED}✗ Chart.yaml not found${NC}"
    exit 1
fi

# Check for required Chart.yaml fields
REQUIRED_FIELDS=("apiVersion" "name" "version" "appVersion")

for field in "${REQUIRED_FIELDS[@]}"; do
    if grep -q "^$field:" "$CHART_PATH/Chart.yaml"; then
        echo -e "${GREEN}✓${NC} $field"
    else
        echo -e "${RED}✗${NC} $field (missing)"
        exit 1
    fi
done

echo ""
echo -e "${YELLOW}Testing with development values...${NC}"
echo ""

# Test with development values
if helm template todo-chatbot "$CHART_PATH" -f "$CHART_PATH/values-dev.yaml" > /dev/null; then
    echo -e "${GREEN}✓ Development values validated${NC}"
else
    echo -e "${RED}✗ Development values validation failed${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Testing with production values...${NC}"
echo ""

# Test with production values
if helm template todo-chatbot "$CHART_PATH" -f "$CHART_PATH/values-prod.yaml" > /dev/null; then
    echo -e "${GREEN}✓ Production values validated${NC}"
else
    echo -e "${RED}✗ Production values validation failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Validation Summary${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${GREEN}✓ Helm lint passed${NC}"
echo -e "${GREEN}✓ Template rendering successful${NC}"
echo -e "${GREEN}✓ All required templates present${NC}"
echo -e "${GREEN}✓ All required values files present${NC}"
echo -e "${GREEN}✓ Chart.yaml validated${NC}"
echo -e "${GREEN}✓ Development values validated${NC}"
echo -e "${GREEN}✓ Production values validated${NC}"
echo ""
echo -e "${GREEN}✓ Chart validation complete - ready for deployment${NC}"
echo ""
echo "Next steps:"
echo "  1. Build Docker images: ./k8s/scripts/build-images.sh"
echo "  2. Load to Minikube: ./k8s/scripts/load-images.sh"
echo "  3. Deploy with Helm: helm install todo-chatbot $CHART_PATH"
