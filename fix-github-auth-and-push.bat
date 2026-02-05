@echo off
REM Fix GitHub Authentication and Push Phase IV

echo ==========================================
echo   Fix GitHub Authentication
echo ==========================================
echo.

echo Current Issue:
echo Git is using credentials for: ahmedturk15943
echo But repository belongs to: Bushraturk
echo.

echo Step 1: Clear old GitHub credentials
echo ==========================================
echo.

REM Clear GitHub credentials from Windows Credential Manager
cmdkey /list | findstr github.com > nul
if %errorlevel% equ 0 (
    echo Found GitHub credentials. Removing...
    cmdkey /delete:LegacyGeneric:target=git:https://github.com
    cmdkey /delete:git:https://github.com
    echo Old credentials removed.
) else (
    echo No cached credentials found.
)
echo.

echo Step 2: Configure Git to use correct account
echo ==========================================
cd /d "%~dp0"
git config user.name "Bushraturk"
git config user.email "your-email@example.com"
echo Git configured for Bushraturk
echo.

echo Step 3: Push to GitHub
echo ==========================================
echo.
echo When prompted, enter your GitHub credentials:
echo   Username: Bushraturk
echo   Password: [Use Personal Access Token, NOT your password]
echo.
echo To create a Personal Access Token:
echo   1. Go to: https://github.com/settings/tokens
echo   2. Click "Generate new token (classic)"
echo   3. Select scopes: repo (all)
echo   4. Copy the token and use it as password
echo.
pause
echo.

echo Pushing to GitHub...
git push -u origin 004-ai-chatbot

if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo   SUCCESS! Code pushed to GitHub
    echo ==========================================
    echo.
    echo Next steps:
    echo 1. Create Pull Request
    echo 2. Follow DEPLOYMENT_READY.md for deployment
    echo.
) else (
    echo.
    echo ==========================================
    echo   Push failed. Try these options:
    echo ==========================================
    echo.
    echo Option 1: Use GitHub Desktop
    echo   - Open GitHub Desktop
    echo   - Sign in with Bushraturk account
    echo   - Push from there
    echo.
    echo Option 2: Use Personal Access Token
    echo   - Create token at: https://github.com/settings/tokens
    echo   - Use token as password when prompted
    echo.
    echo Option 3: Use SSH
    echo   - Set up SSH key
    echo   - Change remote to SSH URL
    echo.
)

pause
