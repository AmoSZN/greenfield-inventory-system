#!/usr/bin/env python3
"""
TEST CLOUD SYNC DIRECTLY
Force sync on the live system and see what happens
"""

import requests
import json
import time

LIVE_URL = "https://greenfield-inventory-system.onrender.com"

def test_cloud_sync():
    print("🔥 TESTING CLOUD SYNC DIRECTLY")
    print("=" * 50)
    
    # Test manual sync
    print("🔄 Triggering manual sync...")
    try:
        response = requests.post(f"{LIVE_URL}/api/paradigm/sync", timeout=120)
        print(f"Sync Response Status: {response.status_code}")
        print(f"Sync Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✅ Sync claims success: {data.get('items_synced')} items")
            else:
                print(f"❌ Sync failed: {data.get('error')}")
        
        # Wait a moment then check stats
        print("\n⏳ Waiting 5 seconds then checking stats...")
        time.sleep(5)
        
        stats_response = requests.get(f"{LIVE_URL}/api/stats")
        print(f"Stats Response: {stats_response.json()}")
        
        # Try a search
        print("\n🔍 Testing search...")
        search_response = requests.get(f"{LIVE_URL}/api/search?q=BEND")
        print(f"Search Response: {search_response.json()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_cloud_sync()
