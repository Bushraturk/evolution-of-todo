#!/bin/bash
# Deployment Verification Script
# Run this after completing deployment to verify everything works

echo "=================================="
echo "Phase IV Deployment Verification"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration (update these with your actual URLs)
MAIN_BACKEND_URL="https://ubushra-todo-app-backend.hf.space"
CHATBOT_BACKEND_URL="https://ubushra-todo-chatbot-backend.hf.space"
FRONTEND_URL="https://YOUR-VERCEL-URL.vercel.app"

echo "Testing with URLs:"
echo "  Main Backend: $MAIN_BACKEND_URL"
echo "  Chatbot Backend: $CHATBOT_BACKEND_URL"
echo "  Frontend: $FRONTEND_URL"
echo ""

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2

    echo -n "Testing $name... "

    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" --max-time 10)

    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✓ OK${NC} (HTTP $response)"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $response)"
        return 1
    fi
}

# Test health endpoints
echo "1. Health Checks"
echo "----------------"
test_endpoint "Main Backend Health" "$MAIN_BACKEND_URL/health"
test_endpoint "Chatbot Backend Health" "$CHATBOT_BACKEND_URL/health"
test_endpoint "Frontend" "$FRONTEND_URL"
echo ""

# Test API documentation
echo "2. API Documentation"
echo "--------------------"
test_endpoint "Main Backend Docs" "$MAIN_BACKEND_URL/docs"
test_endpoint "Chatbot Backend Docs" "$CHATBOT_BACKEND_URL/docs"
echo ""

# Test CORS (basic check)
echo "3. CORS Configuration"
echo "---------------------"
echo -n "Testing CORS headers... "
cors_header=$(curl -s -I -H "Origin: $FRONTEND_URL" "$CHATBOT_BACKEND_URL/health" | grep -i "access-control-allow-origin")
if [ -n "$cors_header" ]; then
    echo -e "${GREEN}✓ OK${NC}"
    echo "  $cors_header"
else
    echo -e "${YELLOW}⚠ WARNING${NC} - CORS headers not found"
fi
echo ""

# Summary
echo "=================================="
echo "Verification Complete"
echo "=================================="
echo ""
echo "Next Steps:"
echo "1. Open $FRONTEND_URL in your browser"
echo "2. Login or register"
echo "3. Look for purple robot icon (bottom-right)"
echo "4. Test chatbot with: 'Add a task to test deployment'"
echo "5. Verify task appears in main task list"
echo ""
echo "If all tests passed, your deployment is successful!"
echo ""
