#!/usr/bin/env python3
"""
Install Greenfield Inventory System as Windows Service
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def install_service():
    """Install the inventory system as a Windows service"""
    
    print("🔧 Installing Greenfield Inventory System as Windows Service")
    print("=" * 70)
    
    # Get current directory
    current_dir = Path.cwd()
    python_exe = sys.executable
    script_path = current_dir / "inventory_system_24_7.py"
    
    print(f"📁 Working Directory: {current_dir}")
    print(f"🐍 Python Executable: {python_exe}")
    print(f"📜 Script Path: {script_path}")
    
    # Install required packages for Windows service
    print("\n1️⃣ Installing Windows service packages...")
    try:
        subprocess.run([python_exe, "-m", "pip", "install", "pywin32", "pywin32-ctypes"], 
                      check=True, capture_output=True)
        print("✅ Service packages installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False
    
    # Create service wrapper
    service_script = current_dir / "inventory_service.py"
    service_code = f'''
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
        os.chdir(r"{current_dir}")
        
        # Start the inventory system
        self.process = subprocess.Popen([
            r"{python_exe}",
            r"{script_path}"
        ])
        
        # Wait for stop signal
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(InventoryService)
'''
    
    print("\n2️⃣ Creating service wrapper...")
    with open(service_script, 'w') as f:
        f.write(service_code)
    print("✅ Service wrapper created")
    
    # Install the service
    print("\n3️⃣ Installing Windows service...")
    try:
        result = subprocess.run([
            python_exe, str(service_script), "install"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Service installed successfully!")
        else:
            print(f"❌ Service installation failed:")
            print(f"   stdout: {result.stdout}")
            print(f"   stderr: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Service installation error: {e}")
        return False
    
    # Start the service
    print("\n4️⃣ Starting the service...")
    try:
        result = subprocess.run([
            python_exe, str(service_script), "start"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Service started successfully!")
        else:
            print(f"⚠️  Service start result: {result.returncode}")
            print(f"   stdout: {result.stdout}")
            print(f"   stderr: {result.stderr}")
    except Exception as e:
        print(f"❌ Service start error: {e}")
    
    print("\n" + "=" * 70)
    print("🎉 INSTALLATION COMPLETE!")
    print("\n📋 Service Details:")
    print("   Name: GreenfieldInventorySystem")
    print("   Display: Greenfield Inventory System - 24/7")
    print("   Status: Should be running")
    print("\n🌐 Access URLs:")
    print("   Local: http://localhost:8000")
    print("   Network: http://192.168.12.78:8000")
    print("\n🔧 Service Management:")
    print("   Start: net start GreenfieldInventorySystem")
    print("   Stop: net stop GreenfieldInventorySystem")
    print("   Remove: python inventory_service.py remove")
    
    return True

if __name__ == "__main__":
    if not install_service():
        print("\n❌ Installation failed!")
        input("Press Enter to exit...")
    else:
        print("\n✅ Installation successful!")
        input("Press Enter to exit...")