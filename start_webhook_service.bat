@echo off
echo ============================================================
echo GREENFIELD METAL SALES - WEBHOOK SERVICE STARTUP
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Navigate to script directory
cd /d "%~dp0"

REM Start the webhook service
echo Starting webhook service on port 5001...
echo.
echo Press Ctrl+C to stop the service
echo.

python webhook_simple_print.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start webhook service
    echo Check the error messages above
    pause
) 