#!/bin/bash

# Phase IV Chatbot - Quick Deployment Script
# This script helps deploy the chatbot to production

echo "=========================================="
echo "  Phase IV Chatbot Deployment Script"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Verify commit
echo -e "${YELLOW}Step 1: Verifying commit...${NC}"
COMMIT=$(git log --oneline -1 | grep "feat: Implement Phase IV")
if [ -z "$COMMIT" ]; then
    echo -e "${RED}Error: Phase IV commit not found!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Commit verified: $COMMIT${NC}"
echo ""

# Step 2: Push to GitHub
echo -e "${YELLOW}Step 2: Pushing to GitHub...${NC}"
echo "Run this command manually:"
echo "  git push -u origin 004-ai-chatbot"
echo ""
read -p "Press Enter after pushing to GitHub..."
echo ""

# Step 3: Create Pull Request
echo -e "${YELLOW}Step 3: Creating Pull Request...${NC}"
echo "Run this command:"
echo '  gh pr create --title "feat: Phase IV AI-Powered Todo Chatbot" --base 002-fullstack-webapp'
echo ""
read -p "Press Enter after creating PR..."
echo ""

# Step 4: Database Migration
echo -e "${YELLOW}Step 4: Database Migration${NC}"
echo "Run the migration on Neon DB:"
echo "  cd phase4-chatbot/backend"
echo "  python run_migration.py"
echo ""
read -p "Press Enter after running migration..."
echo ""

# Step 5: Deploy Chatbot Backend
echo -e "${YELLOW}Step 5: Deploy Chatbot Backend to Hugging Face${NC}"
echo "1. Go to: https://huggingface.co/spaces/Ubushra/todo-chatbot-backend"
echo "2. Upload files from: phase4-chatbot/backend/"
echo "3. Set environment variables (see DEPLOYMENT_READY.md)"
echo ""
read -p "Press Enter after deploying backend..."
echo ""

# Step 6: Update Frontend Environment
echo -e "${YELLOW}Step 6: Update Frontend Environment${NC}"
echo "Update frontend/.env.local with production URLs"
echo "  NEXT_PUBLIC_CHAT_API_URL=https://ubushra-todo-chatbot-backend.hf.space"
echo ""
read -p "Press Enter after updating .env.local..."
echo ""

# Step 7: Deploy Frontend
echo -e "${YELLOW}Step 7: Deploy Frontend to Vercel${NC}"
echo "Run this command:"
echo "  cd frontend"
echo "  vercel --prod"
echo ""
read -p "Press Enter after deploying frontend..."
echo ""

# Step 8: Verify Deployment
echo -e "${YELLOW}Step 8: Verifying Deployment...${NC}"
echo "Testing health endpoints..."
echo ""

# Test main backend
echo -n "Main Backend: "
curl -s https://ubushra-todo-app-backend.hf.space/health > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Online${NC}"
else
    echo -e "${RED}✗ Offline${NC}"
fi

# Test chatbot backend
echo -n "Chatbot Backend: "
curl -s https://ubushra-todo-chatbot-backend.hf.space/health > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Online${NC}"
else
    echo -e "${RED}✗ Offline${NC}"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "  Deployment Complete!"
echo "==========================================${NC}"
echo ""
echo "Next Steps:"
echo "1. Test the chatbot at your frontend URL"
echo "2. Look for the purple robot icon"
echo "3. Send a test message: 'Add a task to test deployment'"
echo "4. Verify the task appears in your task list"
echo ""
echo "Documentation:"
echo "- DEPLOYMENT_READY.md - Complete deployment guide"
echo "- CHATBOT_TESTING_GUIDE.md - Testing instructions"
echo ""
