#!/bin/bash

# Validate resource configuration for Todo Chatbot deployments
# This script checks resource requests, limits, and usage

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="default"
COMPONENTS=("backend" "frontend")

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Validate: Resource Configuration${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    exit 1
fi

# Counters
total_checks=0
passed_checks=0
failed_checks=0
warnings=0

# Function to check resource requests
check_resource_requests() {
    local component=$1

    echo -e "${YELLOW}Checking resource requests for ${component}...${NC}"

    # Get resource requests
    cpu_request=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.containers[0].resources.requests.cpu}' 2>/dev/null)
    memory_request=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.containers[0].resources.requests.memory}' 2>/dev/null)

    total_checks=$((total_checks + 1))

    if [ -z "$cpu_request" ] || [ -z "$memory_request" ]; then
        echo -e "${RED}✗ Resource requests not configured${NC}"
        failed_checks=$((failed_checks + 1))
        return 1
    else
        echo -e "${GREEN}✓ Resource requests configured${NC}"
        echo "  CPU Request: $cpu_request"
        echo "  Memory Request: $memory_request"
        passed_checks=$((passed_checks + 1))
        return 0
    fi
}

# Function to check resource limits
check_resource_limits() {
    local component=$1

    echo -e "${YELLOW}Checking resource limits for ${component}...${NC}"

    # Get resource limits
    cpu_limit=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.containers[0].resources.limits.cpu}' 2>/dev/null)
    memory_limit=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.containers[0].resources.limits.memory}' 2>/dev/null)

    total_checks=$((total_checks + 1))

    if [ -z "$cpu_limit" ] || [ -z "$memory_limit" ]; then
        echo -e "${RED}✗ Resource limits not configured${NC}"
        failed_checks=$((failed_checks + 1))
        return 1
    else
        echo -e "${GREEN}✓ Resource limits configured${NC}"
        echo "  CPU Limit: $cpu_limit"
        echo "  Memory Limit: $memory_limit"
        passed_checks=$((passed_checks + 1))
        return 0
    fi
}

# Function to check resource ratios
check_resource_ratios() {
    local component=$1

    echo -e "${YELLOW}Checking resource request/limit ratios for ${component}...${NC}"

    # Get values
    cpu_request=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.containers[0].resources.requests.cpu}' 2>/dev/null)
    cpu_limit=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.containers[0].resources.limits.cpu}' 2>/dev/null)
    memory_request=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.containers[0].resources.requests.memory}' 2>/dev/null)
    memory_limit=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.containers[0].resources.limits.memory}' 2>/dev/null)

    total_checks=$((total_checks + 1))

    if [ -z "$cpu_request" ] || [ -z "$cpu_limit" ] || [ -z "$memory_request" ] || [ -z "$memory_limit" ]; then
        echo -e "${YELLOW}⚠ Cannot check ratios (resources not fully configured)${NC}"
        warnings=$((warnings + 1))
        return 0
    fi

    # Convert to millicores for CPU
    cpu_request_m=$(echo $cpu_request | sed 's/m//')
    cpu_limit_m=$(echo $cpu_limit | sed 's/m//')

    # Check CPU ratio (limit should be 2-5x request)
    if [ "$cpu_limit_m" -gt $((cpu_request_m * 10)) ]; then
        echo -e "${YELLOW}⚠ CPU limit is much higher than request (${cpu_limit} vs ${cpu_request})${NC}"
        warnings=$((warnings + 1))
    fi

    # Convert memory to Mi
    memory_request_mi=$(echo $memory_request | sed 's/Mi//')
    memory_limit_mi=$(echo $memory_limit | sed 's/Mi//')

    # Check memory ratio (limit should be 1.5-3x request)
    if [ "$memory_limit_mi" -gt $((memory_request_mi * 5)) ]; then
        echo -e "${YELLOW}⚠ Memory limit is much higher than request (${memory_limit} vs ${memory_request})${NC}"
        warnings=$((warnings + 1))
    fi

    echo -e "${GREEN}✓ Resource ratios checked${NC}"
    passed_checks=$((passed_checks + 1))
}

# Function to check actual resource usage
check_resource_usage() {
    local component=$1

    echo -e "${YELLOW}Checking actual resource usage for ${component}...${NC}"

    total_checks=$((total_checks + 1))

    # Check if metrics-server is available
    if ! kubectl top pods -n ${NAMESPACE} &> /dev/null; then
        echo -e "${YELLOW}⚠ Metrics server not available (install with: minikube addons enable metrics-server)${NC}"
        warnings=$((warnings + 1))
        return 0
    fi

    # Get pod name
    pod_name=$(kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/component=${component} -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

    if [ -z "$pod_name" ]; then
        echo -e "${RED}✗ No pod found for ${component}${NC}"
        failed_checks=$((failed_checks + 1))
        return 1
    fi

    # Get usage
    usage=$(kubectl top pod ${pod_name} -n ${NAMESPACE} 2>/dev/null)

    if [ -n "$usage" ]; then
        echo -e "${GREEN}✓ Resource usage available${NC}"
        echo "$usage"
        passed_checks=$((passed_checks + 1))

        # Extract CPU and memory usage
        cpu_usage=$(echo "$usage" | tail -1 | awk '{print $2}')
        memory_usage=$(echo "$usage" | tail -1 | awk '{print $3}')

        # Get requests for comparison
        cpu_request=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.containers[0].resources.requests.cpu}' 2>/dev/null)
        memory_request=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.containers[0].resources.requests.memory}' 2>/dev/null)

        echo "  Requested: CPU ${cpu_request}, Memory ${memory_request}"
        echo "  Using: CPU ${cpu_usage}, Memory ${memory_usage}"
    else
        echo -e "${YELLOW}⚠ Could not get resource usage${NC}"
        warnings=$((warnings + 1))
    fi
}

# Function to check for resource quotas
check_resource_quotas() {
    echo -e "${YELLOW}Checking resource quotas for namespace ${NAMESPACE}...${NC}"

    total_checks=$((total_checks + 1))

    quotas=$(kubectl get resourcequota -n ${NAMESPACE} 2>/dev/null)

    if [ -z "$quotas" ] || echo "$quotas" | grep -q "No resources found"; then
        echo -e "${YELLOW}⚠ No resource quotas defined${NC}"
        echo "  Consider setting quotas for production environments"
        warnings=$((warnings + 1))
    else
        echo -e "${GREEN}✓ Resource quotas defined${NC}"
        echo "$quotas"
        passed_checks=$((passed_checks + 1))
    fi
}

# Function to check for limit ranges
check_limit_ranges() {
    echo -e "${YELLOW}Checking limit ranges for namespace ${NAMESPACE}...${NC}"

    total_checks=$((total_checks + 1))

    limit_ranges=$(kubectl get limitrange -n ${NAMESPACE} 2>/dev/null)

    if [ -z "$limit_ranges" ] || echo "$limit_ranges" | grep -q "No resources found"; then
        echo -e "${YELLOW}⚠ No limit ranges defined${NC}"
        echo "  Consider setting limit ranges for production environments"
        warnings=$((warnings + 1))
    else
        echo -e "${GREEN}✓ Limit ranges defined${NC}"
        echo "$limit_ranges"
        passed_checks=$((passed_checks + 1))
    fi
}

# Function to check node resources
check_node_resources() {
    echo -e "${YELLOW}Checking node resources...${NC}"

    total_checks=$((total_checks + 1))

    # Get node capacity
    echo "Node capacity:"
    kubectl top nodes 2>/dev/null || echo "  (metrics not available)"

    # Get allocatable resources
    echo ""
    echo "Allocatable resources:"
    kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.allocatable.cpu}{"\t"}{.status.allocatable.memory}{"\n"}{end}' | column -t

    passed_checks=$((passed_checks + 1))
}

# Validate each component
for component in "${COMPONENTS[@]}"; do
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Component: ${component}${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    # Check if deployment exists
    if ! kubectl get deployment/${component} -n ${NAMESPACE} &> /dev/null; then
        echo -e "${RED}✗ Deployment ${component} not found${NC}"
        failed_checks=$((failed_checks + 4))
        total_checks=$((total_checks + 4))
        continue
    fi

    # Check resource requests
    check_resource_requests "$component"
    echo ""

    # Check resource limits
    check_resource_limits "$component"
    echo ""

    # Check resource ratios
    check_resource_ratios "$component"
    echo ""

    # Check actual usage
    check_resource_usage "$component"
done

# Check namespace-level resources
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Namespace-Level Resources${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

check_resource_quotas
echo ""

check_limit_ranges
echo ""

check_node_resources

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Validation Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Total Checks: $total_checks"
echo -e "${GREEN}Passed: $passed_checks${NC}"
echo -e "${RED}Failed: $failed_checks${NC}"
echo -e "${YELLOW}Warnings: $warnings${NC}"
echo ""

# Calculate score
if [ $total_checks -gt 0 ]; then
    score=$(awk "BEGIN {printf \"%.0f\", ($passed_checks / $total_checks) * 100}")
    echo "Resource Configuration Score: ${score}/100"
    echo ""
fi

# Recommendations
if [ $failed_checks -gt 0 ] || [ $warnings -gt 0 ]; then
    echo -e "${YELLOW}Recommendations:${NC}"

    if [ $failed_checks -gt 0 ]; then
        echo "  1. Configure resource requests for all containers"
        echo "  2. Configure resource limits for all containers"
        echo "  3. Set reasonable values based on actual usage"
    fi

    if [ $warnings -gt 0 ]; then
        echo "  4. Enable metrics-server for resource monitoring"
        echo "  5. Consider setting resource quotas for namespace"
        echo "  6. Consider setting limit ranges for namespace"
        echo "  7. Review resource request/limit ratios"
        echo "  8. Monitor actual usage and adjust accordingly"
    fi

    echo ""
fi

# Exit with appropriate code
if [ $failed_checks -gt 0 ]; then
    echo -e "${RED}✗ Resource validation failed${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Resource validation passed${NC}"
    exit 0
fi
