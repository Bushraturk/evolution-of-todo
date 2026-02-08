#!/bin/bash

# Test Docker images locally for Todo Chatbot
# This script runs both backend and frontend images locally to verify they work

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKEND_IMAGE="todo-backend"
FRONTEND_IMAGE="todo-frontend"
TAG="${TAG:-latest}"
BACKEND_PORT=8000
FRONTEND_PORT=3000

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Testing Docker Images Locally${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

# Check if images exist
if ! docker images "${BACKEND_IMAGE}:${TAG}" --format "{{.Repository}}" | grep -q "${BACKEND_IMAGE}"; then
    echo -e "${RED}Error: Backend image not found${NC}"
    echo "Please build images first: ./k8s/scripts/build-images.sh"
    exit 1
fi

if ! docker images "${FRONTEND_IMAGE}:${TAG}" --format "{{.Repository}}" | grep -q "${FRONTEND_IMAGE}"; then
    echo -e "${RED}Error: Frontend image not found${NC}"
    echo "Please build images first: ./k8s/scripts/build-images.sh"
    exit 1
fi

# Check if .env files exist
if [ ! -f "phase4-chatbot/backend/.env" ]; then
    echo -e "${YELLOW}Warning: phase4-chatbot/backend/.env not found${NC}"
    echo "Backend will use default environment variables"
fi

if [ ! -f "phase4-chatbot/frontend/.env.local" ]; then
    echo -e "${YELLOW}Warning: phase4-chatbot/frontend/.env.local not found${NC}"
    echo "Frontend will use default environment variables"
fi

echo ""

# Test backend image
echo -e "${YELLOW}Testing backend image...${NC}"
echo "Starting container on port ${BACKEND_PORT}"
echo ""

# Run backend container in detached mode
BACKEND_CONTAINER=$(docker run -d \
    -p ${BACKEND_PORT}:8000 \
    --env-file phase4-chatbot/backend/.env \
    --name todo-backend-test \
    "${BACKEND_IMAGE}:${TAG}" 2>/dev/null || echo "")

if [ -z "$BACKEND_CONTAINER" ]; then
    echo -e "${RED}✗ Failed to start backend container${NC}"
    echo "Trying without env file..."
    BACKEND_CONTAINER=$(docker run -d \
        -p ${BACKEND_PORT}:8000 \
        --name todo-backend-test \
        "${BACKEND_IMAGE}:${TAG}")
fi

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Check if container is running
if docker ps | grep -q todo-backend-test; then
    echo -e "${GREEN}✓ Backend container is running${NC}"

    # Test health endpoint
    echo "Testing health endpoint..."
    if curl -f http://localhost:${BACKEND_PORT}/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend health check passed${NC}"
    else
        echo -e "${YELLOW}⚠ Backend health check failed (may need database connection)${NC}"
    fi

    # Show logs
    echo ""
    echo "Backend logs:"
    docker logs todo-backend-test --tail 10
else
    echo -e "${RED}✗ Backend container failed to start${NC}"
    docker logs todo-backend-test
fi

echo ""

# Test frontend image
echo -e "${YELLOW}Testing frontend image...${NC}"
echo "Starting container on port ${FRONTEND_PORT}"
echo ""

# Run frontend container in detached mode
FRONTEND_CONTAINER=$(docker run -d \
    -p ${FRONTEND_PORT}:3000 \
    --env-file phase4-chatbot/frontend/.env.local \
    --name todo-frontend-test \
    "${FRONTEND_IMAGE}:${TAG}" 2>/dev/null || echo "")

if [ -z "$FRONTEND_CONTAINER" ]; then
    echo -e "${RED}✗ Failed to start frontend container${NC}"
    echo "Trying without env file..."
    FRONTEND_CONTAINER=$(docker run -d \
        -p ${FRONTEND_PORT}:3000 \
        --name todo-frontend-test \
        "${FRONTEND_IMAGE}:${TAG}")
fi

# Wait for frontend to start
echo "Waiting for frontend to start..."
sleep 5

# Check if container is running
if docker ps | grep -q todo-frontend-test; then
    echo -e "${GREEN}✓ Frontend container is running${NC}"

    # Test health endpoint
    echo "Testing health endpoint..."
    if curl -f http://localhost:${FRONTEND_PORT}/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend health check passed${NC}"
    else
        echo -e "${YELLOW}⚠ Frontend health check failed${NC}"
    fi

    # Show logs
    echo ""
    echo "Frontend logs:"
    docker logs todo-frontend-test --tail 10
else
    echo -e "${RED}✗ Frontend container failed to start${NC}"
    docker logs todo-frontend-test
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Test Summary${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Backend:  http://localhost:${BACKEND_PORT}"
echo "Frontend: http://localhost:${FRONTEND_PORT}"
echo ""
echo "Containers are running. Press Ctrl+C to stop and cleanup."
echo ""
echo "To stop containers manually:"
echo "  docker stop todo-backend-test todo-frontend-test"
echo "  docker rm todo-backend-test todo-frontend-test"
echo ""

# Wait for user interrupt
trap cleanup INT

cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping and removing test containers...${NC}"
    docker stop todo-backend-test todo-frontend-test 2>/dev/null || true
    docker rm todo-backend-test todo-frontend-test 2>/dev/null || true
    echo -e "${GREEN}✓ Cleanup complete${NC}"
    exit 0
}

# Keep script running
while true; do
    sleep 1
done
