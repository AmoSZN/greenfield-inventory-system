@echo off
echo ============================================================
echo    CLEANING GIT HISTORY - REMOVING API KEYS
echo ============================================================
echo.

echo Step 1: Creating a new branch without history...
git checkout --orphan clean-branch

echo Step 2: Adding all files to new branch...
git add .

echo Step 3: Committing to new clean branch...
git commit -m "Clean deployment - Greenfield Metal Sales Inventory System"

echo Step 4: Deleting old master branch...
git branch -D master

echo Step 5: Renaming clean branch to master...
git branch -m master

echo Step 6: Force pushing clean history...
git push origin master --force

echo.
echo ============================================================
echo Git history cleaned! API keys removed from history.
echo ============================================================
echo.
echo Next step: Deploy to Render.com
echo.
pause
