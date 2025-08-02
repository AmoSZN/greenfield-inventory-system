@echo off
echo ============================================================
echo 🚀 GREENFIELD INVENTORY SYSTEM - QUICK DEPLOYMENT
echo ============================================================
echo.

echo Step 1: Add your GitHub repository URL
echo Please provide your GitHub repository URL when prompted
echo Example: https://github.com/yourusername/greenfield-inventory-system.git
echo.

set /p REPO_URL="Enter your GitHub repository URL: "

if "%REPO_URL%"=="" (
    echo ❌ No repository URL provided. Exiting...
    pause
    exit /b 1
)

echo.
echo ✅ Repository URL: %REPO_URL%
echo.

echo Step 2: Connecting to GitHub repository...
git remote add origin %REPO_URL%

echo Step 3: Committing latest changes (including bug fix)...
git add .
git commit -m "Production ready with description bug fix - %date% %time%"

echo Step 4: Pushing to GitHub...
git push -u origin master

echo.
echo ============================================================
echo ✅ CODE PUSHED TO GITHUB SUCCESSFULLY!
echo ============================================================
echo.
echo Next steps:
echo 1. Go to https://render.com and sign up/login
echo 2. Click "New +" and select "Web Service"
echo 3. Connect your GitHub repository
echo 4. Use these settings:
echo    - Build Command: pip install -r requirements.txt
echo    - Start Command: python wsgi.py
echo    - Environment: Python 3
echo.
echo Your system will be LIVE worldwide in 5-10 minutes!
echo ============================================================
pause