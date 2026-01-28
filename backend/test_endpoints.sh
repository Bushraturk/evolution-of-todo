#!/bin/bash
# Quick test script for backend endpoints

BACKEND_URL="https://ubushra-todo-app-backend.hf.space"

echo "=================================="
echo "Testing Backend Endpoints"
echo "=================================="

echo -e "\n1. Testing Health Endpoint..."
curl -s "$BACKEND_URL/health" | jq '.' || curl -s "$BACKEND_URL/health"

echo -e "\n\n2. Testing Root Endpoint..."
curl -s "$BACKEND_URL/" | jq '.' || curl -s "$BACKEND_URL/"

echo -e "\n\n3. Testing Registration (will fail if user exists)..."
curl -s -X POST "$BACKEND_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@example.com","password":"Test123456","name":"Test User"}' \
  | jq '.' || curl -s -X POST "$BACKEND_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@example.com","password":"Test123456","name":"Test User"}'

echo -e "\n\n4. Testing Login..."
curl -s -X POST "$BACKEND_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@example.com","password":"Test123456"}' \
  | jq '.' || curl -s -X POST "$BACKEND_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@example.com","password":"Test123456"}'

echo -e "\n\n=================================="
echo "Test Complete"
echo "=================================="
