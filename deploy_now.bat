@echo off
echo ============================================================
echo    GREENFIELD METAL SALES - PRODUCTION DEPLOYMENT
echo ============================================================
echo.

echo 🚀 DEPLOYMENT OPTIONS:
echo.
echo 1. Deploy to Render.com (RECOMMENDED - Free)
echo 2. Deploy to Railway.app (Alternative - Free)
echo 3. Deploy to Heroku (Paid)
echo 4. Test production app locally
echo.

set /p choice="Choose deployment option (1-4): "

if "%choice%"=="1" goto render
if "%choice%"=="2" goto railway
if "%choice%"=="3" goto heroku
if "%choice%"=="4" goto local
goto invalid

:render
echo.
echo 🎯 DEPLOYING TO RENDER.COM
echo.
echo Step 1: Create GitHub repository
echo - Go to github.com and create new repository
echo - Name it: greenfield-inventory-system
echo.
echo Step 2: Push code to GitHub
git init
git add .
git commit -m "Initial production deployment"
echo.
echo Step 3: Connect to GitHub (you'll need to do this manually)
echo git remote add origin https://github.com/YOUR_USERNAME/greenfield-inventory-system.git
echo git push -u origin main
echo.
echo Step 4: Deploy to Render
echo - Go to render.com
echo - Sign up with GitHub
echo - Create new Web Service
echo - Connect your repository
echo - Build Command: pip install -r requirements.txt
echo - Start Command: uvicorn production_app:app --host 0.0.0.0 --port $PORT
echo.
echo Step 5: Set environment variables in Render:
echo PARADIGM_API_KEY=nVPsQFBteV&GEd7*8n0%RliVjksag8
echo PARADIGM_USERNAME=web_admin
echo PARADIGM_PASSWORD=ChangeMe#123!
echo.
echo Your production URL will be: https://your-app-name.onrender.com
echo.
pause
goto end

:railway
echo.
echo 🚂 DEPLOYING TO RAILWAY.APP
echo.
echo Step 1: Go to railway.app
echo Step 2: Sign up with GitHub
echo Step 3: Create new project
echo Step 4: Connect your repository
echo Step 5: Deploy automatically
echo.
pause
goto end

:heroku
echo.
echo 🏗️ DEPLOYING TO HEROKU
echo.
echo Step 1: Install Heroku CLI
echo Step 2: Create Heroku app
echo Step 3: Deploy with git push
echo.
pause
goto end

:local
echo.
echo 🧪 TESTING PRODUCTION APP LOCALLY
echo.
echo Starting production app...
python production_app.py
echo.
echo Production app should be running at: http://localhost:8000
echo.
pause
goto end

:invalid
echo Invalid choice! Please select 1-4.
pause
goto end

:end
echo.
echo ============================================================
echo Deployment guide completed!
echo ============================================================
pause
