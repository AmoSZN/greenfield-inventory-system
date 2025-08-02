#!/usr/bin/env python3
"""
Production Deployment System for Greenfield Inventory
Ensures 24/7 operation with auto-restart, monitoring, and remote access
"""

import os
import sys
import subprocess
import time
import socket
import threading
import logging
from datetime import datetime
import json
import psutil
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductionDeployment:
    def __init__(self):
        self.process = None
        self.monitoring = True
        self.restart_count = 0
        self.start_time = datetime.now()
        
    def check_port_available(self, port=8000):
        """Check if port is available"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result != 0
    
    def kill_existing_processes(self):
        """Kill any existing Python processes on port 8000"""
        logger.info("Checking for existing processes...")
        
        # Kill by port
        for conn in psutil.net_connections():
            if conn.laddr.port == 8000 and conn.status == 'LISTEN':
                try:
                    proc = psutil.Process(conn.pid)
                    proc.terminate()
                    logger.info(f"Terminated process {conn.pid} on port 8000")
                    time.sleep(2)
                except:
                    pass
        
        # Additional cleanup
        try:
            if sys.platform == "win32":
                subprocess.run("taskkill /F /IM python.exe /FI \"WINDOWTITLE eq *hybrid_smart_inventory*\"", 
                             shell=True, capture_output=True)
        except:
            pass
    
    def start_inventory_system(self):
        """Start the hybrid inventory system"""
        try:
            self.kill_existing_processes()
            time.sleep(2)
            
            if not self.check_port_available(8000):
                logger.error("Port 8000 is still in use!")
                return False
            
            logger.info("Starting Hybrid Smart Inventory System...")
            
            # Start the process
            if sys.platform == "win32":
                # Windows: Create new console window
                self.process = subprocess.Popen(
                    [sys.executable, "hybrid_smart_inventory.py"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    cwd=os.getcwd()
                )
            else:
                # Linux/Mac
                self.process = subprocess.Popen(
                    [sys.executable, "hybrid_smart_inventory.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            # Wait for startup
            time.sleep(5)
            
            # Verify it's running
            if self.verify_system_running():
                logger.info("✅ System started successfully!")
                logger.info("🌐 Access at: http://localhost:8000")
                return True
            else:
                logger.error("❌ System failed to start properly")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start system: {str(e)}")
            return False
    
    def verify_system_running(self):
        """Verify the system is responding"""
        try:
            import requests
            response = requests.get("http://localhost:8000", timeout=5)
            return response.status_code == 200
        except:
            # Fallback to socket check
            return not self.check_port_available(8000)
    
    def monitor_system(self):
        """Monitor system health and restart if needed"""
        while self.monitoring:
            try:
                if not self.verify_system_running():
                    logger.warning("System not responding, restarting...")
                    self.restart_count += 1
                    self.start_inventory_system()
                else:
                    # Log health check
                    if self.restart_count == 0 and time.time() % 300 < 30:  # Every 5 minutes
                        logger.info(f"✅ System healthy - Uptime: {datetime.now() - self.start_time}")
                
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Monitor error: {str(e)}")
                time.sleep(30)
    
    def setup_auto_start(self):
        """Setup Windows auto-start on boot"""
        if sys.platform == "win32":
            logger.info("Setting up Windows auto-start...")
            
            # Create startup batch file
            startup_script = f'''@echo off
cd /d "{os.getcwd()}"
start "Greenfield Inventory" python production_deployment.py
'''
            
            startup_path = os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\greenfield_inventory.bat")
            
            with open(startup_path, 'w') as f:
                f.write(startup_script)
            
            logger.info(f"✅ Auto-start configured at: {startup_path}")
            
            # Also create a Windows Task
            task_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <RestartOnFailure>
      <Interval>PT1M</Interval>
      <Count>3</Count>
    </RestartOnFailure>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>python</Command>
      <Arguments>"{os.path.join(os.getcwd(), 'production_deployment.py')}"</Arguments>
      <WorkingDirectory>{os.getcwd()}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''
            
            # Register task
            try:
                with open('inventory_task.xml', 'w', encoding='utf-16') as f:
                    f.write(task_xml)
                
                subprocess.run([
                    'schtasks', '/create', '/tn', 'GreenfieldInventory',
                    '/xml', 'inventory_task.xml', '/f'
                ], capture_output=True)
                
                os.remove('inventory_task.xml')
                logger.info("✅ Windows Task Scheduler configured")
            except Exception as e:
                logger.warning(f"Could not create scheduled task: {str(e)}")
    
    def create_service_wrapper(self):
        """Create a Windows service wrapper"""
        service_script = '''
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import subprocess

class InventoryService(win32serviceutil.ServiceFramework):
    _svc_name_ = "GreenfieldInventory"
    _svc_display_name_ = "Greenfield Inventory System"
    _svc_description_ = "24/7 Inventory Management System"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.process = None
        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        if self.process:
            self.process.terminate()
            
    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.main()
        
    def main(self):
        # Start the inventory system
        self.process = subprocess.Popen([
            sys.executable, 
            os.path.join(os.path.dirname(__file__), "hybrid_smart_inventory.py")
        ])
        
        # Wait for stop signal
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(InventoryService)
'''
        
        with open('inventory_service.py', 'w') as f:
            f.write(service_script)
        
        logger.info("✅ Windows service wrapper created")
    
    def setup_firewall_rules(self):
        """Setup Windows firewall rules for remote access"""
        if sys.platform == "win32":
            logger.info("Configuring Windows Firewall...")
            
            # Add firewall rule
            cmd = [
                'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                'name="Greenfield Inventory System"',
                'dir=in', 'action=allow', 'protocol=TCP',
                'localport=8000', 'profile=any'
            ]
            
            try:
                subprocess.run(cmd, capture_output=True, check=True)
                logger.info("✅ Firewall rule added for port 8000")
            except:
                logger.warning("Could not add firewall rule (may need admin rights)")
    
    def get_local_ip(self):
        """Get local IP address for network access"""
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return local_ip
        except:
            return "127.0.0.1"
    
    def run(self):
        """Main deployment runner"""
        logger.info("=" * 60)
        logger.info("GREENFIELD INVENTORY - PRODUCTION DEPLOYMENT")
        logger.info("=" * 60)
        
        # Setup components
        self.setup_firewall_rules()
        self.setup_auto_start()
        self.create_service_wrapper()
        
        # Start system
        if self.start_inventory_system():
            local_ip = self.get_local_ip()
            
            logger.info("\n✅ SYSTEM DEPLOYED SUCCESSFULLY!")
            logger.info("=" * 60)
            logger.info(f"🌐 Local Access: http://localhost:8000")
            logger.info(f"🌐 Network Access: http://{local_ip}:8000")
            logger.info(f"📱 Mobile Access: http://{local_ip}:8000")
            logger.info("=" * 60)
            logger.info("📊 Features Available:")
            logger.info("  • Smart Search for all 38,998 items")
            logger.info("  • Bulk CSV Import/Export")
            logger.info("  • Real-time inventory updates")
            logger.info("  • Usage analytics")
            logger.info("  • 24/7 automatic monitoring")
            logger.info("=" * 60)
            
            # Start monitoring
            logger.info("\n🔍 Starting health monitoring...")
            self.monitor_system()
        else:
            logger.error("Failed to start system!")
            sys.exit(1)

def signal_handler(sig, frame):
    logger.info("\nShutting down gracefully...")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    # Check if running as admin on Windows
    if sys.platform == "win32":
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            logger.warning("⚠️  Running without admin rights - some features may be limited")
            logger.info("💡 For full features, run as Administrator")
    
    deployment = ProductionDeployment()
    deployment.run()