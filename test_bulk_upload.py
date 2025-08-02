#!/usr/bin/env python3
"""
Test bulk upload functionality
"""
import requests
import time

def test_bulk_upload():
    print("🧪 Testing Bulk Upload Functionality")
    print("=" * 50)
    
    # Check if system is running
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        if response.status_code == 200:
            print("✅ System is running")
        else:
            print("❌ System returned status:", response.status_code)
            return
    except:
        print("❌ System is not accessible. Starting it...")
        import subprocess
        subprocess.Popen(["python", "inventory_system_24_7.py"])
        time.sleep(5)
    
    # Test bulk upload
    print("\n📤 Testing bulk CSV upload...")
    
    with open('test_bulk_comprehensive.csv', 'rb') as f:
        files = {'file': ('test_bulk.csv', f, 'text/csv')}
        response = requests.post('http://localhost:8000/upload-csv', files=files)
    
    if response.status_code == 200:
        print("✅ Bulk upload successful!")
        result = response.json()
        print(f"   - Processed: {result.get('processed', 0)} items")
        print(f"   - Success: {result.get('success', 0)} items")
        print(f"   - Failed: {result.get('failed', 0)} items")
        
        if result.get('errors'):
            print("\n⚠️ Errors encountered:")
            for error in result['errors'][:5]:  # Show first 5 errors
                print(f"   - {error}")
    else:
        print(f"❌ Upload failed with status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
    
    # Check history
    print("\n📊 Checking update history...")
    response = requests.get('http://localhost:8000/api/history')
    if response.status_code == 200:
        history = response.json()
        print(f"✅ Found {len(history)} recent updates")
        for item in history[:3]:  # Show last 3
            print(f"   - {item['product_id']}: {item['status']} at {item['timestamp']}")
    
    print("\n✅ Bulk upload test complete!")
    print("🌐 View results at: http://localhost:8000/history")

if __name__ == "__main__":
    test_bulk_upload()