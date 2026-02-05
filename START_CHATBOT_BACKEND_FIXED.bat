@echo off
echo ========================================
echo Starting Chatbot Backend (Port 8002)
echo ========================================
echo.

cd /d "%~dp0phase4-chatbot\backend"

echo Current directory: %CD%
echo.

echo Checking if .env file exists...
if not exist .env (
    echo ERROR: .env file not found!
    echo Please create .env file in phase4-chatbot\backend directory
    pause
    exit /b 1
)
echo .env file found!
echo.

echo Starting uvicorn server...
echo API will be available at: http://localhost:8002
echo API Docs will be available at: http://localhost:8002/docs
echo.
echo Press CTRL+C to stop the server
echo.

uvicorn src.main:app --reload --port 8002
