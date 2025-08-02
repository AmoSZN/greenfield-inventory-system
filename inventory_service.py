
import sys
import os
import win32serviceutil
import win32service
import win32event
import subprocess
import time

class InventoryService(win32serviceutil.ServiceFramework):
    _svc_name_ = "GreenfieldInventorySystem"
    _svc_display_name_ = "Greenfield Inventory System - 24/7"
    _svc_description_ = "AI-powered inventory management system with Paradigm ERP integration"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.process = None
        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        if self.process:
            self.process.terminate()
        win32event.SetEvent(self.hWaitStop)
        
    def SvcDoRun(self):
        # Change to the script directory
        os.chdir(r"C:\Users\mattm\OneDrive\Greenfield Metal Sales\Barcode Scanner")
        
        # Start the inventory system
        self.process = subprocess.Popen([
            r"C:\Python313\python.exe",
            r"C:\Users\mattm\OneDrive\Greenfield Metal Sales\Barcode Scanner\inventory_system_24_7.py"
        ])
        
        # Wait for stop signal
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(InventoryService)
