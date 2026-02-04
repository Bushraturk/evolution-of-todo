@echo off
echo ========================================
echo   EVOLUTION OF TODO - FULL STACK START
echo ========================================
echo.
echo Starting 3 servers:
echo   1. Main Backend (Port 8001) - Auth ^& Tasks
echo   2. Chatbot Backend (Port 8002) - AI Chat
echo   3. Frontend (Port 3000) - Web UI
echo.
echo ========================================
echo.

echo Step 1: Stopping all existing processes...
taskkill /F /IM node.exe 2>nul
taskkill /F /IM python.exe 2>nul
timeout /t 2 >nul

echo.
echo Step 2: Starting Main Backend (Port 8001)...
cd /d "%~dp0backend"
start "Main Backend (8001)" cmd /k "uvicorn src.main:app --reload --port 8001"

timeout /t 3 >nul

echo.
echo Step 3: Starting Chatbot Backend (Port 8002)...
cd /d "%~dp0phase4-chatbot\backend"
start "Chatbot Backend (8002)" cmd /k "uvicorn src.main:app --reload --port 8002"

timeout /t 3 >nul

echo.
echo Step 4: Starting Frontend (Port 3000)...
cd /d "%~dp0frontend"
start "Frontend (3000)" cmd /k "npm run dev"

timeout /t 5 >nul

echo.
echo Step 5: Opening browser...
start http://localhost:3000

echo.
echo ========================================
echo   ALL SERVERS STARTED!
echo ========================================
echo.
echo Main Backend:    http://localhost:8001
echo Chatbot Backend: http://localhost:8002
echo Frontend:        http://localhost:3000
echo API Docs:        http://localhost:8001/docs
echo.
echo Look for the purple robot icon after logging in!
echo.
pause
