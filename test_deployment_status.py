#!/usr/bin/env python3
"""
Test Deployment Status - Verify our fixes are working
"""
import requests
import json
import time

def test_deployment():
    """Test the deployment status and functionality"""
    
    # You'll need to replace this with your actual Render URL
    base_url = "https://your-render-app-name.onrender.com"  # Replace with actual URL
    
    print("🔍 Testing Greenfield Inventory System Deployment")
    print("=" * 50)
    
    endpoints_to_test = [
        ("/health", "Health Check"),
        ("/api/health", "API Health Check"),
        ("/api/debug", "Debug Information"),
        ("/api/stats", "System Statistics")
    ]
    
    for endpoint, description in endpoints_to_test:
        try:
            url = base_url + endpoint
            print(f"\n📡 Testing {description}: {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {description}: SUCCESS (Status: {response.status_code})")
                
                if endpoint == "/api/debug":
                    data = response.json()
                    print(f"   📊 Database exists: {data.get('database_exists', 'Unknown')}")
                    print(f"   📄 CSV file exists: {data.get('csv_file_exists', 'Unknown')}")
                    print(f"   📦 Total items: {data.get('database_stats', {}).get('total_items', 'Unknown')}")
                    print(f"   📁 Current directory: {data.get('current_directory', 'Unknown')}")
                
                elif endpoint == "/api/stats":
                    data = response.json()
                    print(f"   📊 Items loaded: {data.get('items_loaded', 'Unknown')}")
                    print(f"   🔄 Updates today: {data.get('updates_today', 'Unknown')}")
                    
            else:
                print(f"❌ {description}: FAILED (Status: {response.status_code})")
                print(f"   Response: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {description}: ERROR - {str(e)}")
        except Exception as e:
            print(f"❌ {description}: UNEXPECTED ERROR - {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("1. Replace 'your-render-app-name' in the base_url with your actual Render app name")
    print("2. Run this script to test your deployment")
    print("3. Check the debug endpoint to verify database and CSV loading")
    print("4. Test search functionality with product IDs like '1015B'")

if __name__ == "__main__":
    test_deployment() 