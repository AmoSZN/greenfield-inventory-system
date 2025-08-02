#!/usr/bin/env python3
"""
Simple 24/7 setup - creates shortcuts and startup files
"""

import os
import sys
from pathlib import Path

def create_24_7_setup():
    """Create simple 24/7 setup"""
    
    print("🔧 Creating 24/7 Inventory System Setup")
    print("=" * 50)
    
    current_dir = Path.cwd()
    python_exe = sys.executable
    script_path = current_dir / "inventory_system_24_7.py"
    
    # Create startup batch file
    batch_file = current_dir / "START_INVENTORY_SYSTEM.bat"
    batch_content = f"""@echo off
title Greenfield Inventory System - 24/7
cd /d "{current_dir}"
echo.
echo ============================================================
echo 🏭 GREENFIELD INVENTORY SYSTEM - STARTING...
echo ============================================================
echo 🌐 Will be available at: http://localhost:8000
echo 📱 Network access at: http://192.168.12.78:8000
echo ============================================================
echo.
"{python_exe}" "{script_path}"
echo.
echo ============================================================
echo 🛑 SYSTEM STOPPED
echo ============================================================
pause
"""
    
    print("1️⃣ Creating startup script...")
    with open(batch_file, 'w') as f:
        f.write(batch_content)
    print(f"✅ Created: {batch_file}")
    
    # Create instructions file
    instructions_file = current_dir / "24_7_INSTRUCTIONS.txt"
    instructions_content = f"""
GREENFIELD INVENTORY SYSTEM - 24/7 SETUP INSTRUCTIONS
=====================================================

🚀 TO START THE SYSTEM:
   Double-click: START_INVENTORY_SYSTEM.bat

🌐 ACCESS URLS:
   Local Computer: http://localhost:8000
   Network Access: http://192.168.12.78:8000
   Mobile Devices: http://192.168.12.78:8000

🔄 FOR AUTO-START ON WINDOWS BOOT:
   1. Right-click START_INVENTORY_SYSTEM.bat
   2. Select "Create shortcut"
   3. Cut the shortcut (Ctrl+X)
   4. Press Win+R, type: shell:startup
   5. Paste the shortcut there (Ctrl+V)

📋 SYSTEM FEATURES:
   ✅ Search 39,193 products
   ✅ Update descriptions (syncs to Paradigm)
   ⚠️  Update quantities (local tracking only)
   ✅ Bulk CSV import/export
   ✅ Complete update history
   ✅ Natural language commands

🛑 TO STOP THE SYSTEM:
   Close the command window or press Ctrl+C

📞 SUPPORT:
   System runs on: {python_exe}
   Script location: {script_path}
   Data folder: {current_dir}/Data/

🎯 QUICK TEST:
   1. Start the system
   2. Open http://localhost:8000
   3. Search for "1015B"
   4. Try updating the description
"""
    
    print("2️⃣ Creating instructions...")
    with open(instructions_file, 'w') as f:
        f.write(instructions_content)
    print(f"✅ Created: {instructions_file}")
    
    print("\n" + "=" * 50)
    print("🎉 24/7 SETUP COMPLETE!")
    print("\n📋 Files Created:")
    print(f"   🚀 {batch_file}")
    print(f"   📖 {instructions_file}")
    
    print("\n🔄 NEXT STEPS:")
    print("   1. Double-click START_INVENTORY_SYSTEM.bat")
    print("   2. System will start at http://localhost:8000")
    print("   3. Read 24_7_INSTRUCTIONS.txt for auto-startup")
    
    # Test if we can start it now
    print(f"\n❓ Start the system now? (y/n): ", end="")
    response = input().lower().strip()
    
    if response in ['y', 'yes']:
        print("🚀 Starting system...")
        os.system(f'"{batch_file}"')
    else:
        print("✅ Setup complete! Start manually when ready.")

if __name__ == "__main__":
    create_24_7_setup()