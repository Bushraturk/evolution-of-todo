#!/bin/bash

# Validate health checks for Todo Chatbot deployments
# This script checks liveness, readiness, and startup probes

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
echo -e "${BLUE}Validate: Health Checks${NC}"
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

# Function to check probe configuration
check_probe_config() {
    local component=$1
    local probe_type=$2

    echo -e "${YELLOW}Checking ${probe_type} probe for ${component}...${NC}"

    # Get probe configuration
    probe_config=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath="{.spec.template.spec.containers[0].${probe_type}Probe}" 2>/dev/null)

    total_checks=$((total_checks + 1))

    if [ -z "$probe_config" ] || [ "$probe_config" = "null" ]; then
        echo -e "${RED}✗ ${probe_type} probe not configured${NC}"
        failed_checks=$((failed_checks + 1))
        return 1
    else
        echo -e "${GREEN}✓ ${probe_type} probe configured${NC}"

        # Show probe details
        echo "  Configuration:"
        kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath="{.spec.template.spec.containers[0].${probe_type}Probe}" | jq '.'

        passed_checks=$((passed_checks + 1))
        return 0
    fi
}

# Function to test probe endpoint
test_probe_endpoint() {
    local component=$1
    local port=$2
    local path=$3

    echo -e "${YELLOW}Testing health endpoint for ${component}...${NC}"

    # Get pod name
    pod_name=$(kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/component=${component} -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

    total_checks=$((total_checks + 1))

    if [ -z "$pod_name" ]; then
        echo -e "${RED}✗ No pod found for ${component}${NC}"
        failed_checks=$((failed_checks + 1))
        return 1
    fi

    # Test endpoint
    if kubectl exec ${pod_name} -n ${NAMESPACE} -- curl -f -s -o /dev/null -w "%{http_code}" http://localhost:${port}${path} 2>/dev/null | grep -q "200"; then
        echo -e "${GREEN}✓ Health endpoint responding (200 OK)${NC}"
        passed_checks=$((passed_checks + 1))
        return 0
    else
        echo -e "${RED}✗ Health endpoint not responding or returning error${NC}"
        failed_checks=$((failed_checks + 1))
        return 1
    fi
}

# Function to check probe timing
check_probe_timing() {
    local component=$1
    local probe_type=$2

    echo -e "${YELLOW}Checking ${probe_type} probe timing for ${component}...${NC}"

    # Get timing values
    initial_delay=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath="{.spec.template.spec.containers[0].${probe_type}Probe.initialDelaySeconds}" 2>/dev/null)
    period=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath="{.spec.template.spec.containers[0].${probe_type}Probe.periodSeconds}" 2>/dev/null)
    timeout=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath="{.spec.template.spec.containers[0].${probe_type}Probe.timeoutSeconds}" 2>/dev/null)
    failure_threshold=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath="{.spec.template.spec.containers[0].${probe_type}Probe.failureThreshold}" 2>/dev/null)

    total_checks=$((total_checks + 1))

    # Check if values are reasonable
    issues=0

    if [ -n "$initial_delay" ] && [ "$initial_delay" -lt 5 ]; then
        echo -e "${YELLOW}⚠ initialDelaySeconds ($initial_delay) might be too short${NC}"
        warnings=$((warnings + 1))
        issues=$((issues + 1))
    fi

    if [ -n "$timeout" ] && [ "$timeout" -lt 1 ]; then
        echo -e "${YELLOW}⚠ timeoutSeconds ($timeout) might be too short${NC}"
        warnings=$((warnings + 1))
        issues=$((issues + 1))
    fi

    if [ -n "$failure_threshold" ] && [ "$failure_threshold" -lt 3 ]; then
        echo -e "${YELLOW}⚠ failureThreshold ($failure_threshold) might be too low${NC}"
        warnings=$((warnings + 1))
        issues=$((issues + 1))
    fi

    if [ $issues -eq 0 ]; then
        echo -e "${GREEN}✓ Probe timing looks reasonable${NC}"
        echo "  initialDelaySeconds: $initial_delay"
        echo "  periodSeconds: $period"
        echo "  timeoutSeconds: $timeout"
        echo "  failureThreshold: $failure_threshold"
        passed_checks=$((passed_checks + 1))
    else
        echo -e "${YELLOW}⚠ Probe timing has warnings (see above)${NC}"
        passed_checks=$((passed_checks + 1))
    fi
}

# Function to check probe failures
check_probe_failures() {
    local component=$1

    echo -e "${YELLOW}Checking for recent probe failures for ${component}...${NC}"

    total_checks=$((total_checks + 1))

    # Get recent events related to probes
    probe_failures=$(kubectl get events -n ${NAMESPACE} \
        --field-selector involvedObject.kind=Pod \
        --sort-by='.lastTimestamp' \
        | grep -i "unhealthy\|liveness\|readiness" \
        | grep ${component} \
        | tail -5)

    if [ -z "$probe_failures" ]; then
        echo -e "${GREEN}✓ No recent probe failures${NC}"
        passed_checks=$((passed_checks + 1))
        return 0
    else
        echo -e "${YELLOW}⚠ Recent probe failures detected:${NC}"
        echo "$probe_failures"
        warnings=$((warnings + 1))
        passed_checks=$((passed_checks + 1))
        return 0
    fi
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
        failed_checks=$((failed_checks + 3))
        total_checks=$((total_checks + 3))
        continue
    fi

    # Determine port and path based on component
    if [ "$component" = "backend" ]; then
        port=8000
        path="/health"
    else
        port=3000
        path="/api/health"
    fi

    # Check liveness probe
    check_probe_config "$component" "liveness"
    check_probe_timing "$component" "liveness"

    echo ""

    # Check readiness probe
    check_probe_config "$component" "readiness"
    check_probe_timing "$component" "readiness"

    echo ""

    # Check startup probe (optional)
    startup_probe=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath="{.spec.template.spec.containers[0].startupProbe}" 2>/dev/null)
    if [ -n "$startup_probe" ] && [ "$startup_probe" != "null" ]; then
        check_probe_config "$component" "startup"
        check_probe_timing "$component" "startup"
        echo ""
    fi

    # Test health endpoint
    test_probe_endpoint "$component" "$port" "$path"

    echo ""

    # Check for probe failures
    check_probe_failures "$component"
done

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
    echo "Health Check Score: ${score}/100"
    echo ""
fi

# Recommendations
if [ $failed_checks -gt 0 ] || [ $warnings -gt 0 ]; then
    echo -e "${YELLOW}Recommendations:${NC}"

    if [ $failed_checks -gt 0 ]; then
        echo "  1. Configure missing health probes (liveness, readiness)"
        echo "  2. Implement health check endpoints in application code"
        echo "  3. Ensure health endpoints return proper HTTP status codes"
    fi

    if [ $warnings -gt 0 ]; then
        echo "  4. Review probe timing configuration"
        echo "  5. Increase initialDelaySeconds if pods need more startup time"
        echo "  6. Increase failureThreshold to avoid premature restarts"
        echo "  7. Investigate recent probe failures"
    fi

    echo ""
fi

# Exit with appropriate code
if [ $failed_checks -gt 0 ]; then
    echo -e "${RED}✗ Health check validation failed${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Health check validation passed${NC}"
    exit 0
fi
