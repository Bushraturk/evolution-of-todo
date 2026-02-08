#!/bin/bash

# Validate security configuration for Todo Chatbot deployments
# This script checks security contexts, network policies, and secrets

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
echo -e "${BLUE}Validate: Security Configuration${NC}"
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

# Function to check security context
check_security_context() {
    local component=$1

    echo -e "${YELLOW}Checking security context for ${component}...${NC}"

    # Check runAsNonRoot
    run_as_non_root=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.securityContext.runAsNonRoot}' 2>/dev/null)

    total_checks=$((total_checks + 1))

    if [ "$run_as_non_root" = "true" ]; then
        echo -e "${GREEN}✓ Running as non-root user${NC}"
        passed_checks=$((passed_checks + 1))
    else
        echo -e "${RED}✗ Not configured to run as non-root user${NC}"
        failed_checks=$((failed_checks + 1))
    fi

    # Check runAsUser
    run_as_user=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.securityContext.runAsUser}' 2>/dev/null)

    total_checks=$((total_checks + 1))

    if [ -n "$run_as_user" ] && [ "$run_as_user" != "0" ]; then
        echo -e "${GREEN}✓ Running as user ID: ${run_as_user}${NC}"
        passed_checks=$((passed_checks + 1))
    else
        echo -e "${YELLOW}⚠ User ID not specified or running as root${NC}"
        warnings=$((warnings + 1))
    fi

    # Check fsGroup
    fs_group=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.securityContext.fsGroup}' 2>/dev/null)

    total_checks=$((total_checks + 1))

    if [ -n "$fs_group" ]; then
        echo -e "${GREEN}✓ File system group set: ${fs_group}${NC}"
        passed_checks=$((passed_checks + 1))
    else
        echo -e "${YELLOW}⚠ File system group not set${NC}"
        warnings=$((warnings + 1))
    fi
}

# Function to check container security context
check_container_security_context() {
    local component=$1

    echo -e "${YELLOW}Checking container security context for ${component}...${NC}"

    # Check allowPrivilegeEscalation
    allow_privilege_escalation=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.containers[0].securityContext.allowPrivilegeEscalation}' 2>/dev/null)

    total_checks=$((total_checks + 1))

    if [ "$allow_privilege_escalation" = "false" ]; then
        echo -e "${GREEN}✓ Privilege escalation disabled${NC}"
        passed_checks=$((passed_checks + 1))
    else
        echo -e "${YELLOW}⚠ Privilege escalation not explicitly disabled${NC}"
        warnings=$((warnings + 1))
    fi

    # Check readOnlyRootFilesystem
    read_only_root=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.containers[0].securityContext.readOnlyRootFilesystem}' 2>/dev/null)

    total_checks=$((total_checks + 1))

    if [ "$read_only_root" = "true" ]; then
        echo -e "${GREEN}✓ Read-only root filesystem enabled${NC}"
        passed_checks=$((passed_checks + 1))
    else
        echo -e "${YELLOW}⚠ Read-only root filesystem not enabled${NC}"
        warnings=$((warnings + 1))
    fi

    # Check capabilities
    capabilities=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.containers[0].securityContext.capabilities}' 2>/dev/null)

    total_checks=$((total_checks + 1))

    if [ -n "$capabilities" ] && echo "$capabilities" | grep -q "drop"; then
        echo -e "${GREEN}✓ Capabilities configured${NC}"
        echo "  Capabilities: $capabilities"
        passed_checks=$((passed_checks + 1))
    else
        echo -e "${YELLOW}⚠ Capabilities not configured (consider dropping ALL)${NC}"
        warnings=$((warnings + 1))
    fi
}

# Function to check network policies
check_network_policies() {
    echo -e "${YELLOW}Checking network policies for namespace ${NAMESPACE}...${NC}"

    total_checks=$((total_checks + 1))

    network_policies=$(kubectl get networkpolicies -n ${NAMESPACE} 2>/dev/null)

    if [ -z "$network_policies" ] || echo "$network_policies" | grep -q "No resources found"; then
        echo -e "${YELLOW}⚠ No network policies defined${NC}"
        echo "  Consider restricting network access with NetworkPolicy resources"
        warnings=$((warnings + 1))
    else
        echo -e "${GREEN}✓ Network policies defined${NC}"
        echo "$network_policies"
        passed_checks=$((passed_checks + 1))
    fi
}

# Function to check secrets
check_secrets() {
    echo -e "${YELLOW}Checking secrets configuration...${NC}"

    total_checks=$((total_checks + 1))

    # Check if todo-secrets exists
    if kubectl get secret todo-secrets -n ${NAMESPACE} &> /dev/null; then
        echo -e "${GREEN}✓ Required secrets exist${NC}"

        # Check secret keys
        secret_keys=$(kubectl get secret todo-secrets -n ${NAMESPACE} -o jsonpath='{.data}' | jq -r 'keys[]')
        echo "  Secret keys: $(echo $secret_keys | tr '\n' ', ')"

        passed_checks=$((passed_checks + 1))
    else
        echo -e "${RED}✗ Required secrets not found${NC}"
        failed_checks=$((failed_checks + 1))
    fi

    # Check for secrets in environment variables (anti-pattern)
    total_checks=$((total_checks + 1))

    for component in "${COMPONENTS[@]}"; do
        env_vars=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.containers[0].env[*].value}' 2>/dev/null)

        if echo "$env_vars" | grep -qiE "password|secret|key|token" 2>/dev/null; then
            echo -e "${RED}✗ Potential secrets in environment variables for ${component}${NC}"
            failed_checks=$((failed_checks + 1))
            return 1
        fi
    done

    echo -e "${GREEN}✓ No hardcoded secrets in environment variables${NC}"
    passed_checks=$((passed_checks + 1))
}

# Function to check service account
check_service_account() {
    local component=$1

    echo -e "${YELLOW}Checking service account for ${component}...${NC}"

    total_checks=$((total_checks + 1))

    service_account=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.serviceAccountName}' 2>/dev/null)

    if [ -n "$service_account" ] && [ "$service_account" != "default" ]; then
        echo -e "${GREEN}✓ Custom service account configured: ${service_account}${NC}"
        passed_checks=$((passed_checks + 1))
    else
        echo -e "${YELLOW}⚠ Using default service account${NC}"
        echo "  Consider creating dedicated service accounts for production"
        warnings=$((warnings + 1))
    fi

    # Check automountServiceAccountToken
    automount=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.automountServiceAccountToken}' 2>/dev/null)

    total_checks=$((total_checks + 1))

    if [ "$automount" = "false" ]; then
        echo -e "${GREEN}✓ Service account token automount disabled${NC}"
        passed_checks=$((passed_checks + 1))
    else
        echo -e "${YELLOW}⚠ Service account token automount not disabled${NC}"
        echo "  Consider disabling if not needed"
        warnings=$((warnings + 1))
    fi
}

# Function to check pod security policies
check_pod_security_policies() {
    echo -e "${YELLOW}Checking pod security policies...${NC}"

    total_checks=$((total_checks + 1))

    # Check for PodSecurityPolicy (deprecated in K8s 1.25+)
    psp=$(kubectl get psp 2>/dev/null)

    if [ -z "$psp" ] || echo "$psp" | grep -q "No resources found"; then
        echo -e "${YELLOW}⚠ No pod security policies defined${NC}"
        echo "  Note: PodSecurityPolicy is deprecated. Consider using Pod Security Standards"
        warnings=$((warnings + 1))
    else
        echo -e "${GREEN}✓ Pod security policies defined${NC}"
        passed_checks=$((passed_checks + 1))
    fi
}

# Function to check image pull policy
check_image_pull_policy() {
    local component=$1

    echo -e "${YELLOW}Checking image pull policy for ${component}...${NC}"

    total_checks=$((total_checks + 1))

    image_pull_policy=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.containers[0].imagePullPolicy}' 2>/dev/null)

    if [ "$image_pull_policy" = "Always" ] || [ "$image_pull_policy" = "IfNotPresent" ]; then
        echo -e "${GREEN}✓ Image pull policy: ${image_pull_policy}${NC}"
        passed_checks=$((passed_checks + 1))
    else
        echo -e "${YELLOW}⚠ Image pull policy not set or set to Never${NC}"
        warnings=$((warnings + 1))
    fi

    # Check image tag
    image=$(kubectl get deployment/${component} -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.containers[0].image}' 2>/dev/null)

    total_checks=$((total_checks + 1))

    if echo "$image" | grep -q ":latest"; then
        echo -e "${YELLOW}⚠ Using 'latest' tag: ${image}${NC}"
        echo "  Consider using specific version tags for production"
        warnings=$((warnings + 1))
    else
        echo -e "${GREEN}✓ Using specific image tag: ${image}${NC}"
        passed_checks=$((passed_checks + 1))
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
        failed_checks=$((failed_checks + 5))
        total_checks=$((total_checks + 5))
        continue
    fi

    # Check security context
    check_security_context "$component"
    echo ""

    # Check container security context
    check_container_security_context "$component"
    echo ""

    # Check service account
    check_service_account "$component"
    echo ""

    # Check image pull policy
    check_image_pull_policy "$component"
done

# Check cluster-level security
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Cluster-Level Security${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

check_network_policies
echo ""

check_secrets
echo ""

check_pod_security_policies

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
    echo "Security Configuration Score: ${score}/100"
    echo ""
fi

# Recommendations
if [ $failed_checks -gt 0 ] || [ $warnings -gt 0 ]; then
    echo -e "${YELLOW}Recommendations:${NC}"

    if [ $failed_checks -gt 0 ]; then
        echo "  1. Configure security contexts for all containers"
        echo "  2. Run containers as non-root users"
        echo "  3. Create and use Kubernetes secrets for sensitive data"
        echo "  4. Never hardcode secrets in environment variables"
    fi

    if [ $warnings -gt 0 ]; then
        echo "  5. Enable read-only root filesystem where possible"
        echo "  6. Drop unnecessary Linux capabilities"
        echo "  7. Create network policies to restrict traffic"
        echo "  8. Use dedicated service accounts"
        echo "  9. Disable service account token automount if not needed"
        echo "  10. Use specific image tags instead of 'latest'"
        echo "  11. Consider implementing Pod Security Standards"
    fi

    echo ""
fi

# Exit with appropriate code
if [ $failed_checks -gt 0 ]; then
    echo -e "${RED}✗ Security validation failed${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Security validation passed${NC}"
    exit 0
fi
