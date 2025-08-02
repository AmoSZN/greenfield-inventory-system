@echo off
echo ============================================================
echo GREENFIELD METAL SALES - PRE-DEPLOYMENT CHECKLIST
echo ============================================================
echo.

REM Kill any running Python processes
echo [1/5] Stopping existing processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul

REM Check if running as admin
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [2/5] Administrator rights: YES
) else (
    echo [2/5] Administrator rights: NO - REQUIRED FOR SERVICE INSTALL!
    echo Please run as Administrator
    pause
    exit /b 1
)

REM Check BarTender
echo [3/5] Checking BarTender...
if exist "C:\Program Files\Seagull\BarTender 11.4\BarTend.exe" (
    echo       BarTender: FOUND
) else (
    echo       BarTender: NOT FOUND!
    pause
    exit /b 1
)

REM Test simple webhook
echo [4/5] Testing webhook...
start /MIN python webhook_simple_print.py
timeout /t 5 >nul
curl -s http://localhost:5001/health >nul 2>&1
if %errorLevel% == 0 (
    echo       Webhook: WORKING
) else (
    echo       Webhook: FAILED!
    pause
    exit /b 1
)
taskkill /F /IM python.exe >nul 2>&1

REM Check NSSM
echo [5/5] Checking NSSM...
where nssm >nul 2>&1
if %errorLevel% == 0 (
    echo       NSSM: FOUND
) else (
    echo       NSSM: NOT FOUND - Downloading...
    powershell -Command "Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile 'nssm.zip'"
    powershell -Command "Expand-Archive -Path 'nssm.zip' -DestinationPath '.'"
    copy nssm-2.24\win64\nssm.exe C:\Windows\System32\
    del nssm.zip
    rmdir /S /Q nssm-2.24
)

echo.
echo ============================================================
echo ALL CHECKS PASSED - READY FOR DEPLOYMENT!
echo ============================================================
echo.
echo Next: Run install_as_service.bat
echo.
pause 