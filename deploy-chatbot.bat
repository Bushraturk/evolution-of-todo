@echo off
REM Phase IV Chatbot - Quick Deployment Script for Windows
REM This script helps deploy the chatbot to production

echo ==========================================
echo   Phase IV Chatbot Deployment Script
echo ==========================================
echo.

REM Step 1: Verify commit
echo Step 1: Verifying commit...
git log --oneline -1 | findstr "feat: Implement Phase IV" > nul
if errorlevel 1 (
    echo [ERROR] Phase IV commit not found!
    pause
    exit /b 1
)
echo [OK] Commit verified
echo.

REM Step 2: Push to GitHub
echo Step 2: Pushing to GitHub...
echo Run this command manually:
echo   git push -u origin 004-ai-chatbot
echo.
pause
echo.

REM Step 3: Create Pull Request
echo Step 3: Creating Pull Request...
echo Run this command:
echo   gh pr create --title "feat: Phase IV AI-Powered Todo Chatbot" --base 002-fullstack-webapp
echo.
pause
echo.

REM Step 4: Database Migration
echo Step 4: Database Migration
echo Run the migration on Neon DB:
echo   cd phase4-chatbot\backend
echo   python run_migration.py
echo.
pause
echo.

REM Step 5: Deploy Chatbot Backend
echo Step 5: Deploy Chatbot Backend to Hugging Face
echo 1. Go to: https://huggingface.co/spaces/Ubushra/todo-chatbot-backend
echo 2. Upload files from: phase4-chatbot\backend\
echo 3. Set environment variables (see DEPLOYMENT_READY.md)
echo.
pause
echo.

REM Step 6: Update Frontend Environment
echo Step 6: Update Frontend Environment
echo Update frontend\.env.local with production URLs
echo   NEXT_PUBLIC_CHAT_API_URL=https://ubushra-todo-chatbot-backend.hf.space
echo.
pause
echo.

REM Step 7: Deploy Frontend
echo Step 7: Deploy Frontend to Vercel
echo Run this command:
echo   cd frontend
echo   vercel --prod
echo.
pause
echo.

REM Step 8: Verify Deployment
echo Step 8: Verifying Deployment...
echo Testing health endpoints...
echo.

curl -s https://ubushra-todo-app-backend.hf.space/health > nul 2>&1
if errorlevel 1 (
    echo Main Backend: [OFFLINE]
) else (
    echo Main Backend: [ONLINE]
)

curl -s https://ubushra-todo-chatbot-backend.hf.space/health > nul 2>&1
if errorlevel 1 (
    echo Chatbot Backend: [OFFLINE]
) else (
    echo Chatbot Backend: [ONLINE]
)

echo.
echo ==========================================
echo   Deployment Complete!
echo ==========================================
echo.
echo Next Steps:
echo 1. Test the chatbot at your frontend URL
echo 2. Look for the purple robot icon
echo 3. Send a test message: 'Add a task to test deployment'
echo 4. Verify the task appears in your task list
echo.
echo Documentation:
echo - DEPLOYMENT_READY.md - Complete deployment guide
echo - CHATBOT_TESTING_GUIDE.md - Testing instructions
echo.
pause
