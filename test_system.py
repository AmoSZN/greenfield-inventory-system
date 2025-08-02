#!/usr/bin/env python3
"""
Quick test to verify the inventory system is working
"""

import requests
import time
import sys

def test_system():
    print("🔍 Testing Greenfield Inventory System...")
    print("=" * 50)
    
    # Test 1: Basic connectivity
    print("Test 1: Checking if system is running...")
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        if response.status_code == 200:
            print("✅ System is running!")
            print(f"   Response size: {len(response.text)} bytes")
        else:
            print(f"❌ System returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to system: {str(e)}")
        return False
    
    # Test 2: API endpoints
    print("\nTest 2: Testing API endpoints...")
    endpoints = [
        "/api/stats",
        "/api/frequent-items",
        "/api/recent-updates"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
            else:
                print(f"❌ {endpoint} - Status {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {str(e)}")
    
    # Test 3: Search functionality
    print("\nTest 3: Testing search...")
    try:
        response = requests.get("http://localhost:8000/api/search?q=1030", timeout=5)
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Search works! Found {len(results)} results")
        else:
            print(f"❌ Search failed with status: {response.status_code}")
    except Exception as e:
        print(f"❌ Search error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("\n📌 Access your system at: http://localhost:8000")
    return True

if __name__ == "__main__":
    # Install requests if needed
    try:
        import requests
    except ImportError:
        print("Installing requests module...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests
    
    test_system()