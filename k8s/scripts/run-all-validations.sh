#!/bin/bash

# Run all validation scripts for Todo Chatbot deployment
# This script executes health checks, resource validation, and security validation

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Run All Validations${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Running comprehensive validation suite for Todo Chatbot deployment"
echo ""

# Counters
total_validations=0
passed_validations=0
failed_validations=0

# Function to run validation script
run_validation() {
    local script_name=$1
    local description=$2

    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}${description}${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    total_validations=$((total_validations + 1))

    if [ -f "${SCRIPT_DIR}/${script_name}" ]; then
        if bash "${SCRIPT_DIR}/${script_name}"; then
            echo ""
            echo -e "${GREEN}✓ ${description} passed${NC}"
            passed_validations=$((passed_validations + 1))
            return 0
        else
            echo ""
            echo -e "${RED}✗ ${description} failed${NC}"
            failed_validations=$((failed_validations + 1))
            return 1
        fi
    else
        echo -e "${RED}✗ Validation script not found: ${script_name}${NC}"
        failed_validations=$((failed_validations + 1))
        return 1
    fi

    echo ""
}

# Run all validation scripts
echo -e "${YELLOW}Starting validation suite...${NC}"
echo ""

# 1. Health Checks Validation
run_validation "validate-health-checks.sh" "Health Checks Validation"
echo ""

# 2. Resource Configuration Validation
run_validation "validate-resources.sh" "Resource Configuration Validation"
echo ""

# 3. Security Configuration Validation
run_validation "validate-security.sh" "Security Configuration Validation"
echo ""

# Overall Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Overall Validation Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Total Validations: $total_validations"
echo -e "${GREEN}Passed: $passed_validations${NC}"
echo -e "${RED}Failed: $failed_validations${NC}"
echo ""

# Calculate overall score
if [ $total_validations -gt 0 ]; then
    overall_score=$(awk "BEGIN {printf \"%.0f\", ($passed_validations / $total_validations) * 100}")
    echo "Overall Score: ${overall_score}/100"
    echo ""
fi

# Production readiness assessment
if [ $failed_validations -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ PRODUCTION READY${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "All validation checks passed!"
    echo "Your deployment meets production readiness criteria."
    echo ""
    echo "Next steps:"
    echo "  1. Review PRODUCTION_READINESS.md for additional considerations"
    echo "  2. Set up monitoring and alerting"
    echo "  3. Configure backup and disaster recovery"
    echo "  4. Document runbooks for common operations"
    echo "  5. Plan for Phase VI: Cloud deployment"
    echo ""
    exit 0
else
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}⚠ NOT PRODUCTION READY${NC}"
    echo -e "${YELLOW}========================================${NC}"
    echo ""
    echo "Some validation checks failed."
    echo "Please address the issues before deploying to production."
    echo ""
    echo "Review the output above for specific recommendations."
    echo "See PRODUCTION_READINESS.md for detailed guidance."
    echo ""
    exit 1
fi
