@echo off
echo ============================================================
echo    GREENFIELD METAL SALES - IMMEDIATE RENDER DEPLOYMENT
echo ============================================================
echo.
echo ✅ GitHub Repository: https://github.com/AmoSZN/greenfield-inventory-system
echo ✅ Code Successfully Pushed
echo.
echo 🚀 DEPLOYMENT STEPS:
echo.
echo 1. OPEN YOUR WEB BROWSER
echo 2. GO TO: https://render.com
echo 3. CLICK: "Sign Up" (if you don't have an account)
echo 4. CLICK: "New +" → "Web Service"
echo 5. CONNECT: GitHub repository
echo 6. SELECT: greenfield-inventory-system
echo.
echo 📋 CONFIGURATION SETTINGS:
echo.
echo Name: greenfield-inventory-system
echo Environment: Python 3
echo Build Command: pip install -r requirements.txt
echo Start Command: uvicorn production_app:app --host 0.0.0.0 --port $PORT
echo.
echo 🔧 ENVIRONMENT VARIABLES:
echo.
echo PARADIGM_API_KEY=nVPsQFBteV&GEd7*8n0%RliVjksag8
echo PARADIGM_USERNAME=web_admin
echo PARADIGM_PASSWORD=ChangeMe#123!
echo DATABASE_URL=sqlite:///./data/smart_inventory.db
echo PYTHON_VERSION=3.11.0
echo.
echo ⏱️  DEPLOYMENT TIME: ~10-15 minutes
echo.
echo 📱 AFTER DEPLOYMENT:
echo - Your system will be available 24/7
echo - URL will be: https://greenfield-inventory-system.onrender.com
echo - Update Paradigm webhook with the new URL
echo.
echo Press any key to open Render.com in your browser...
pause >nul
start https://render.com
echo.
echo ============================================================
echo Deployment instructions displayed!
echo ============================================================
pause
