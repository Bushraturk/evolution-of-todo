@echo off
REM Interactive GitHub Push Script
REM This will prompt you for credentials

echo ==========================================
echo   GitHub Push - Phase IV Chatbot
echo ==========================================
echo.

cd /d "%~dp0"

echo Clearing old credentials...
cmdkey /delete:LegacyGeneric:target=git:https://github.com >nul 2>&1
cmdkey /delete:git:https://github.com >nul 2>&1
echo Old credentials cleared.
echo.

echo Setting Git user to Bushraturk...
git config user.name "Bushraturk"
echo.

echo ==========================================
echo   IMPORTANT: When prompted for credentials
echo ==========================================
echo.
echo Username: Bushraturk
echo Password: [Your GitHub password or Personal Access Token]
echo.
echo NOTE: If you don't have a Personal Access Token:
echo 1. Go to: https://github.com/settings/tokens
echo 2. Click "Generate new token (classic)"
echo 3. Select "repo" scope
echo 4. Copy the token and use it as password
echo.
echo Press any key to start push...
pause >nul
echo.

echo Pushing to GitHub...
echo.
git push -u origin 004-ai-chatbot

if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo   SUCCESS! Code pushed to GitHub
    echo ==========================================
    echo.
    echo Branch: 004-ai-chatbot
    echo Commit: 9409148
    echo.
    echo Next steps:
    echo 1. Create Pull Request
    echo 2. Follow DEPLOYMENT_READY.md
    echo.
) else (
    echo.
    echo ==========================================
    echo   Push Failed
    echo ==========================================
    echo.
    echo Possible reasons:
    echo 1. Wrong username or password
    echo 2. Need to use Personal Access Token instead of password
    echo 3. Account doesn't have push access
    echo.
    echo Solutions:
    echo 1. Create Personal Access Token at: https://github.com/settings/tokens
    echo 2. Use GitHub Desktop (easier)
    echo 3. Check GITHUB_AUTH_FIX.md for detailed help
    echo.
)

pause
