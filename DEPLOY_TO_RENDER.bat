@echo off
echo 🚀 GREENFIELD INVENTORY SYSTEM - RENDER DEPLOYMENT
echo ===================================================
echo.
echo ✅ Checking deployment readiness...
echo.

REM Check if all required files exist
if not exist "app.py" (
    echo ❌ ERROR: app.py not found!
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ❌ ERROR: requirements.txt not found!
    pause
    exit /b 1
)

if not exist "inventory_system_24_7.py" (
    echo ❌ ERROR: inventory_system_24_7.py not found!
    pause
    exit /b 1
)

echo ✅ All required files found!
echo.

REM Check git status
echo 📋 Checking Git status...
git status --porcelain
echo.

REM Push to GitHub if needed
echo 🔄 Pushing to GitHub...
git add .
git commit -m "Prepare for Render deployment"
git push origin master

echo.
echo 🎉 DEPLOYMENT READY!
echo ===================
echo.
echo 📋 NEXT STEPS:
echo 1. Go to https://render.com
echo 2. Sign up with GitHub account
echo 3. Click "New +" → "Web Service"
echo 4. Connect repository: AmoSZN/greenfield-ai-suite
echo 5. Configure with these settings:
echo    - Name: greenfield-inventory-system
echo    - Environment: Python 3
echo    - Build Command: pip install -r requirements.txt
echo    - Start Command: python app.py
echo 6. Add environment variables (see RENDER_DEPLOYMENT_GUIDE.md)
echo 7. Click "Create Web Service"
echo.
echo 📖 For detailed instructions, see: RENDER_DEPLOYMENT_GUIDE.md
echo.
pause 