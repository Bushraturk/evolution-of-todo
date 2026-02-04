@echo off
echo ========================================
echo   CHATBOT QUICK START - PORT 8002
echo ========================================
echo.

echo Step 1: Stopping all processes...
taskkill /F /IM node.exe 2>nul
taskkill /F /IM python.exe 2>nul
timeout /t 2 >nul

echo.
echo Step 2: Starting Phase IV Chatbot Backend (Port 8002)...
echo.
cd /d "%~dp0phase4-chatbot\backend"
start "Chatbot Backend (8002)" cmd /k "uvicorn src.main:app --reload --port 8002"

timeout /t 3 >nul

echo.
echo Step 3: Starting Frontend (Port 3000)...
echo.
cd /d "%~dp0frontend"
start "Frontend (3000)" cmd /k "npm run dev"

timeout /t 5 >nul

echo.
echo Step 4: Opening browser...
start http://localhost:3000

echo.
echo ========================================
echo   DONE! Check your browser
echo ========================================
echo.
echo Backend: http://localhost:8002
echo Frontend: http://localhost:3000
echo.
echo Look for purple robot icon in bottom-right corner!
echo.
pause
