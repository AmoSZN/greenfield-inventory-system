@echo off
echo ============================================================
echo    🚀 IMMEDIATE PRODUCTION DEPLOYMENT
echo ============================================================
echo.
echo This will deploy the fixed system to Render.com
echo Production URL: https://greenfield-inventory-system.onrender.com
echo.

echo Step 1: Updating production files...
echo.

REM Update render.yaml for production
echo services: > render.yaml
echo   - type: web >> render.yaml
echo     name: greenfield-inventory-system >> render.yaml
echo     env: python >> render.yaml
echo     buildCommand: pip install -r requirements.txt >> render.yaml
echo     startCommand: uvicorn production_app:app --host 0.0.0.0 --port $PORT >> render.yaml
echo     envVars: >> render.yaml
echo       - key: PARADIGM_API_KEY >> render.yaml
echo         value: nVPsQFBteV^&GEd7*8n0%%RliVjksag8 >> render.yaml
echo       - key: PARADIGM_USERNAME >> render.yaml
echo         value: web_admin >> render.yaml
echo       - key: PARADIGM_PASSWORD >> render.yaml
echo         value: ChangeMe#123! >> render.yaml

echo Step 2: Pushing to GitHub...
echo.

REM Add all files
git add .

REM Commit changes
git commit -m "Fix production Paradigm integration - deploy immediately"

REM Push to GitHub
git push origin master --force

echo.
echo Step 3: Deploying to Render...
echo.

echo ✅ DEPLOYMENT INITIATED!
echo.
echo 🌐 Production URL: https://greenfield-inventory-system.onrender.com
echo.
echo 📋 Next steps:
echo 1. Wait 2-3 minutes for deployment to complete
echo 2. Test the production system
echo 3. Configure Paradigm webhook
echo 4. Test live inventory updates
echo.
echo 🔗 Render Dashboard: https://dashboard.render.com
echo.

pause
