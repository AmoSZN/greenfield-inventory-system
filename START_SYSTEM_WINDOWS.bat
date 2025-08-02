@echo off
echo.
echo ============================================================
echo           GREENFIELD METAL SALES
echo       Hybrid Smart Inventory System v2.0
echo.
echo   Managing 38,998 items with intelligent search
echo ============================================================
echo.
echo Starting system...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from python.org
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Checking dependencies...
pip install fastapi uvicorn[standard] httpx aiosqlite python-multipart

REM Create directories
if not exist "data" mkdir data
if not exist "cache" mkdir cache  
if not exist "exports" mkdir exports

echo.
echo ============================================================
echo System starting...
echo Access the system at: http://localhost:8000
echo Press Ctrl+C to stop
echo ============================================================
echo.

REM Start the system
python hybrid_smart_inventory.py