@echo off
echo ============================================================
echo    FIXING SECURITY ISSUES AND PUSHING TO GITHUB
echo ============================================================
echo.

echo Step 1: Adding security fixes...
git add .

echo Step 2: Committing security fixes...
git commit -m "Security fix: Remove API keys from documentation"

echo Step 3: Pushing to GitHub...
git push origin master --force

echo.
echo ============================================================
echo Security issues fixed and code pushed to GitHub!
echo ============================================================
echo.
echo Next step: Deploy to Render.com
echo.
pause
