@echo off
echo ============================================================
echo Starting Chatbot Backend Server
echo ============================================================
echo.
echo Server will start on http://127.0.0.1:8002
echo API Docs: http://127.0.0.1:8002/docs
echo Press CTRL+C to stop the server
echo.
echo ============================================================
echo.

cd /d "%~dp0phase4-chatbot\backend"

if not exist .env (
    echo ERROR: .env file not found in phase4-chatbot\backend!
    echo Please create .env file with required configuration.
    pause
    exit /b 1
)

echo Starting server from: %CD%
echo.
uvicorn src.main:app --reload --port 8002
