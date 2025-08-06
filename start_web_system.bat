@echo off
echo ============================================================
echo    STARTING GREENFIELD INVENTORY WEB SYSTEM
echo ============================================================

echo.
echo Stopping any existing Python processes...
taskkill /f /im python.exe 2>nul

echo.
echo Waiting 3 seconds for processes to stop...
timeout /t 3 /nobreak >nul

echo.
echo Starting inventory system on port 8001...
echo Access at: http://localhost:8001
echo.
echo Press Ctrl+C to stop the system
echo.

python start_system_fixed.py

pause
