#!/usr/bin/env python3
"""
Force deployment by updating version and triggering rebuild
"""

import os
import time
from datetime import datetime

def update_version():
    """Update version to force deployment"""
    # Read current production app with UTF-8 encoding
    with open('production_app_fixed.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update version to force deployment
    new_version = f"v2.2-{int(time.time())}"
    content = content.replace('"version": "2.1"', f'"version": "{new_version}"')
    content = content.replace('Production Inventory Management System v2.1', f'Production Inventory Management System {new_version}')
    
    # Write updated file with UTF-8 encoding
    with open('production_app_fixed.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated version to {new_version}")
    return new_version

def create_deployment_trigger():
    """Create a trigger file to force deployment"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    trigger_content = f"""
# DEPLOYMENT TRIGGER - {timestamp}
# This file forces Render.com to rebuild the application

DEPLOYMENT_TIMESTAMP = "{timestamp}"
FORCE_REBUILD = True
VERSION = "2.2-{int(time.time())}"

# Render.com will detect this change and trigger a new deployment
"""
    
    with open('DEPLOYMENT_TRIGGER.txt', 'w', encoding='utf-8') as f:
        f.write(trigger_content)
    
    print(f"✅ Created deployment trigger: {timestamp}")

if __name__ == "__main__":
    print("🚀 FORCING PRODUCTION DEPLOYMENT")
    print("=" * 50)
    
    # Update version
    new_version = update_version()
    
    # Create trigger
    create_deployment_trigger()
    
    print(f"\n📦 Ready to deploy version: {new_version}")
    print("Next: git add . && git commit && git push")

