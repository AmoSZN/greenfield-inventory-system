@echo off
echo.
echo ============================================================
echo     GREENFIELD INVENTORY - 24/7 SERVICE INSTALLER
echo ============================================================
echo.
echo This will install the inventory system as a Windows service
echo that starts automatically on boot.
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ERROR: Administrator privileges required!
    echo Please run this script as Administrator.
    echo.
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install flask requests werkzeug pywin32

echo.
echo Creating Windows service...

REM Create service wrapper
echo import win32serviceutil > service_wrapper.py
echo import win32service >> service_wrapper.py
echo import win32event >> service_wrapper.py
echo import servicemanager >> service_wrapper.py
echo import socket >> service_wrapper.py
echo import sys >> service_wrapper.py
echo import os >> service_wrapper.py
echo import subprocess >> service_wrapper.py
echo. >> service_wrapper.py
echo class InventoryService(win32serviceutil.ServiceFramework): >> service_wrapper.py
echo     _svc_name_ = "GreenfieldInventory" >> service_wrapper.py
echo     _svc_display_name_ = "Greenfield Inventory System" >> service_wrapper.py
echo     _svc_description_ = "24/7 Inventory Management System for 38,998 items" >> service_wrapper.py
echo. >> service_wrapper.py
echo     def __init__(self, args): >> service_wrapper.py
echo         win32serviceutil.ServiceFramework.__init__(self, args) >> service_wrapper.py
echo         self.hWaitStop = win32event.CreateEvent(None, 0, 0, None) >> service_wrapper.py
echo         self.process = None >> service_wrapper.py
echo. >> service_wrapper.py
echo     def SvcStop(self): >> service_wrapper.py
echo         self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING) >> service_wrapper.py
echo         win32event.SetEvent(self.hWaitStop) >> service_wrapper.py
echo         if self.process: >> service_wrapper.py
echo             self.process.terminate() >> service_wrapper.py
echo. >> service_wrapper.py
echo     def SvcDoRun(self): >> service_wrapper.py
echo         servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, >> service_wrapper.py
echo                               servicemanager.PYS_SERVICE_STARTED, >> service_wrapper.py
echo                               (self._svc_name_, '')) >> service_wrapper.py
echo         self.main() >> service_wrapper.py
echo. >> service_wrapper.py
echo     def main(self): >> service_wrapper.py
echo         # Start the inventory system >> service_wrapper.py
echo         self.process = subprocess.Popen([sys.executable, >> service_wrapper.py
echo                                          os.path.join(os.path.dirname(__file__), >> service_wrapper.py
echo                                                       "inventory_system_24_7.py")]) >> service_wrapper.py
echo         # Wait for stop signal >> service_wrapper.py
echo         win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE) >> service_wrapper.py
echo. >> service_wrapper.py
echo if __name__ == '__main__': >> service_wrapper.py
echo     win32serviceutil.HandleCommandLine(InventoryService) >> service_wrapper.py

echo.
echo Installing service...
python service_wrapper.py install

echo.
echo Configuring service to start automatically...
sc config GreenfieldInventory start= auto

echo.
echo Starting service...
python service_wrapper.py start

echo.
echo Adding firewall rule for remote access...
netsh advfirewall firewall add rule name="Greenfield Inventory System" dir=in action=allow protocol=TCP localport=8000 profile=any

echo.
echo ============================================================
echo     ✅ SERVICE INSTALLATION COMPLETE!
echo ============================================================
echo.
echo The inventory system is now running as a Windows service.
echo.
echo Access your system at:
echo   • Local: http://localhost:8000
echo   • Network: http://%COMPUTERNAME%:8000
echo.
echo Service Management:
echo   • Stop:    net stop GreenfieldInventory
echo   • Start:   net start GreenfieldInventory
echo   • Remove:  python service_wrapper.py remove
echo.
echo The service will start automatically when Windows boots.
echo.
pause