@echo off
echo ============================================================
echo    PUSHING CODE TO GITHUB
echo ============================================================
echo.
echo Repository: https://github.com/AmoSZN/greenfield-inventory-system
echo.

echo Step 1: Setting remote origin...
git remote set-url origin https://github.com/AmoSZN/greenfield-inventory-system.git

echo Step 2: Adding all files...
git add .

echo Step 3: Committing changes...
git commit -m "Production deployment - Greenfield Metal Sales Inventory System"

echo Step 4: Pushing to GitHub...
git push origin master --force

echo.
echo ============================================================
echo Code pushed to GitHub successfully!
echo ============================================================
echo.
echo Next step: Deploy to Render.com
echo.
pause
