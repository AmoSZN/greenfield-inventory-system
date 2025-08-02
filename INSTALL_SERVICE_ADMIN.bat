@echo off
REM Run this as Administrator to install the Inventory AI as a Windows Service

echo.
echo ==================================================================
echo GREENFIELD INVENTORY AI - SERVICE INSTALLER
echo ==================================================================
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo [1/5] Stopping any existing Python processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 3 /nobreak >nul

echo [2/5] Creating service wrapper script...
echo import subprocess > service_wrapper.py
echo import sys >> service_wrapper.py
echo import os >> service_wrapper.py
echo os.chdir(r'%CD%') >> service_wrapper.py
echo subprocess.run([sys.executable, 'inventory_system_24_7.py']) >> service_wrapper.py

echo [3/5] Installing Python service dependencies...
pip install pywin32 >nul 2>&1

echo [4/5] Creating Windows Task Scheduler entry...
schtasks /create /tn "GreenfieldInventoryAI" /tr "\"%CD%\python.exe\" \"%CD%\inventory_system_24_7.py\"" /sc onstart /ru SYSTEM /rl highest /f

echo [5/5] Starting the service...
schtasks /run /tn "GreenfieldInventoryAI"

echo.
echo ==================================================================
echo ✅ SERVICE INSTALLATION COMPLETE!
echo ==================================================================
echo.
echo The Greenfield Inventory AI is now running as a Windows service!
echo.
echo - Starts automatically on boot
echo - Runs in background 24/7
echo - Access at: http://localhost:8000
echo.
echo To manage the service:
echo - Stop: schtasks /end /tn "GreenfieldInventoryAI"
echo - Start: schtasks /run /tn "GreenfieldInventoryAI"
echo - Remove: schtasks /delete /tn "GreenfieldInventoryAI" /f
echo.
pause