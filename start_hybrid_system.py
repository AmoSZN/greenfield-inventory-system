#!/usr/bin/env python3
"""
Quick Start Script for Hybrid Smart Inventory System
Ensures all dependencies are installed and starts the system
"""

import subprocess
import sys
import os
import time

def print_banner():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                 GREENFIELD METAL SALES                       ║
    ║            Hybrid Smart Inventory System v2.0                ║
    ║                                                              ║
    ║  Managing 38,998 items with intelligent search & caching     ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def check_and_install_dependencies():
    """Check and install required packages"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn[standard]',
        'httpx',
        'aiosqlite',
        'python-multipart'
    ]
    
    for package in required_packages:
        try:
            __import__(package.split('[')[0].replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"📦 Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully")

def create_directories():
    """Create necessary directories"""
    directories = ['data', 'cache', 'exports']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Created directory: {directory}")

def start_system():
    """Start the hybrid inventory system"""
    print("\n🚀 Starting Hybrid Smart Inventory System...")
    print("=" * 60)
    print("📌 Access the system at: http://localhost:8000")
    print("=" * 60)
    print("\n💡 Quick Tips:")
    print("  • Start typing any Product ID to search")
    print("  • System learns from your usage patterns")
    print("  • Import CSV for bulk loading (optional)")
    print("  • All 38,998 items accessible on-demand")
    print("\n🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Start the server
    subprocess.run([sys.executable, "hybrid_smart_inventory.py"])

def main():
    print_banner()
    
    try:
        # Check Python version
        if sys.version_info < (3, 7):
            print("❌ Python 3.7+ is required")
            sys.exit(1)
        
        # Install dependencies
        check_and_install_dependencies()
        
        # Create directories
        create_directories()
        
        # Start the system
        start_system()
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
        print("Thank you for using Greenfield Smart Inventory System!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Please check the error message and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()