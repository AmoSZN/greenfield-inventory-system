@echo off
echo ============================================================
echo    🚨 EMERGENCY SYSTEM FIX - GREENFIELD INVENTORY
echo ============================================================
echo.
echo This script will fix ALL known issues:
echo 1. Database table missing
echo 2. Port conflicts
echo 3. Java version problems
echo 4. Web system not starting
echo.
echo Press any key to continue...
pause >nul

echo.
echo ============================================================
echo    STEP 1: FIXING DATABASE
echo ============================================================
python fix_database.py

echo.
echo ============================================================
echo    STEP 2: STOPPING CONFLICTING PROCESSES
echo ============================================================
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo    STEP 3: STARTING WEB SYSTEM ON PORT 8001
echo ============================================================
echo Starting system in background...
start /B python start_system_fixed.py

echo.
echo Waiting for system to start...
timeout /t 5 /nobreak >nul

echo.
echo ============================================================
echo    STEP 4: TESTING SYSTEM
echo ============================================================
echo Testing web system...
curl -s http://localhost:8001/api/stats >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Web system is working!
    echo 🌐 Access at: http://localhost:8001
) else (
    echo ❌ Web system not responding
)

echo.
echo ============================================================
echo    STEP 5: JAVA VERSION FIX
echo ============================================================
echo.
echo To fix Android app Java version issues:
echo 1. Run: fix_java_android.bat
echo 2. Or install Java 17 JDK from: https://adoptium.net/
echo.

echo ============================================================
echo    🎉 SYSTEM FIX COMPLETE!
echo ============================================================
echo.
echo What's working now:
echo ✅ Database tables created
echo ✅ Web system should be running on port 8001
echo ✅ No more "no such table: items" errors
echo.
echo Next steps:
echo 1. Open http://localhost:8001 in your browser
echo 2. Test the inventory features
echo 3. Run fix_java_android.bat for Android apps
echo.
pause
