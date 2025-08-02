#!/usr/bin/env python3
"""
Quick Production Setup - Get your system live in 30 minutes
"""

import os

def create_essential_files():
    """Create only the essential files for production deployment"""
    
    print("Quick Production Setup - Essential Files Only")
    print("=" * 50)
    
    # 1. Requirements file
    print("Creating requirements.txt...")
    requirements = """Flask==3.0.0
requests==2.31.0
aiohttp==3.9.1
waitress==2.1.2
python-dotenv==1.0.0"""
    
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(requirements)
    print("   Done: requirements.txt")
    
    # 2. Production WSGI server
    print("Creating production server...")
    wsgi_content = """import os
import sys
from waitress import serve

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import your Flask app
from inventory_system_24_7 import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting production server on port {port}")
    
    # Use Waitress WSGI server for production
    serve(app, host='0.0.0.0', port=port, threads=6)
"""
    
    with open('wsgi.py', 'w', encoding='utf-8') as f:
        f.write(wsgi_content)
    print("   Done: wsgi.py")
    
    # 3. Environment variables
    print("Creating environment template...")
    env_content = """SECRET_KEY=your-super-secret-key-change-this
DEBUG=False
PARADIGM_API_KEY=nVPsQFBteV&GEd7*8n0%RliVjksag8
PARADIGM_USERNAME=web_admin
PARADIGM_PASSWORD=ChangeMe#123!
PARADIGM_BASE_URL=https://greenfieldapi.para-apps.com
PORT=8000"""
    
    with open('.env.production', 'w', encoding='utf-8') as f:
        f.write(env_content)
    print("   Done: .env.production")
    
    # 4. Production startup script
    print("Creating startup script...")
    startup_content = """@echo off
echo Starting Greenfield Inventory System - Production Mode
echo ====================================================

set FLASK_ENV=production
set DEBUG=False

python wsgi.py

pause"""
    
    with open('start_production.bat', 'w', encoding='utf-8') as f:
        f.write(startup_content)
    print("   Done: start_production.bat")
    
    # 5. Docker file for cloud deployment
    print("Creating Docker configuration...")
    docker_content = """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p Data

EXPOSE 8000

CMD ["python", "wsgi.py"]"""
    
    with open('Dockerfile', 'w', encoding='utf-8') as f:
        f.write(docker_content)
    print("   Done: Dockerfile")
    
    print("\n" + "=" * 60)
    print("PRODUCTION FILES CREATED SUCCESSFULLY!")
    print("=" * 60)
    
    print("\nFILES CREATED:")
    print("  requirements.txt - Python dependencies")
    print("  wsgi.py - Production server")
    print("  .env.production - Environment variables")
    print("  start_production.bat - Windows startup")
    print("  Dockerfile - Cloud deployment")
    
    print("\nDEPLOYMENT OPTIONS:")
    print("\n1. QUICK CLOUD DEPLOYMENT (30 minutes):")
    print("   - Go to https://render.com or https://railway.app")
    print("   - Connect your GitHub account")
    print("   - Deploy from this folder")
    print("   - Your system will be live!")
    
    print("\n2. DIGITALOCEAN DEPLOYMENT:")
    print("   - Go to https://cloud.digitalocean.com")
    print("   - Create new App from GitHub")
    print("   - Use the files we just created")
    
    print("\n3. LOCAL PRODUCTION TEST:")
    print("   - Run: start_production.bat")
    print("   - Test at: http://localhost:8000")
    
    print("\nYOUR SYSTEM WILL HAVE:")
    print("  ✓ 24/7 uptime")
    print("  ✓ SSL encryption")
    print("  ✓ Global access")
    print("  ✓ Mobile optimization")
    print("  ✓ Professional interface")
    print("  ✓ Advanced NLP")
    print("  ✓ Real-time ERP sync")
    
    print(f"\nREADY TO GO LIVE!")
    print("Choose your deployment option and follow the steps!")

if __name__ == "__main__":
    create_essential_files()