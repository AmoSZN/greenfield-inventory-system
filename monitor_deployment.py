#!/usr/bin/env python3
"""
MONITOR DEPLOYMENT STATUS
Track deployment progress and verify system is using latest code
"""

import requests
import time
import json
from datetime import datetime

LIVE_URL = "https://greenfield-inventory-system.onrender.com"

def monitor_deployment():
    print("🔥 MONITORING DEPLOYMENT STATUS")
    print("=" * 60)
    
    # Check current version and status
    for attempt in range(10):
        try:
            print(f"\n📡 Attempt {attempt + 1}/10 - {datetime.now().strftime('%H:%M:%S')}")
            
            # Health check
            health_response = requests.get(f"{LIVE_URL}/health", timeout=30)
            if health_response.status_code == 200:
                health_data = health_response.json()
                print(f"✅ Health: {health_data.get('status')} - Version: {health_data.get('version')}")
                print(f"🔗 Paradigm Connected: {health_data.get('paradigm_connected')}")
            else:
                print(f"❌ Health check failed: {health_response.status_code}")
                continue
            
            # Test sync endpoint with detailed response
            print("🔄 Testing sync endpoint...")
            sync_response = requests.post(f"{LIVE_URL}/api/paradigm/sync", timeout=120)
            print(f"📊 Sync Status: {sync_response.status_code}")
            
            if sync_response.status_code == 200:
                sync_data = sync_response.json()
                print(f"📋 Sync Response: {json.dumps(sync_data, indent=2)}")
                
                # If sync shows success, check stats
                if sync_data.get("success"):
                    print("✅ Sync reports success! Checking stats...")
                    time.sleep(2)
                    
                    stats_response = requests.get(f"{LIVE_URL}/api/stats")
                    if stats_response.status_code == 200:
                        stats_data = stats_response.json()
                        print(f"📊 Stats: {json.dumps(stats_data, indent=2)}")
                        
                        if stats_data.get("total_items", 0) > 0:
                            print("🎉 SUCCESS! Database has items!")
                            return True
                    
                elif sync_data.get("error"):
                    print(f"❌ Sync error: {sync_data.get('error')}")
                else:
                    print("⚠️ Sync response unclear")
            else:
                print(f"❌ Sync endpoint failed: {sync_response.status_code}")
            
            print(f"⏳ Waiting 30 seconds before next attempt...")
            time.sleep(30)
            
        except Exception as e:
            print(f"❌ Error on attempt {attempt + 1}: {e}")
            time.sleep(10)
    
    print("❌ All attempts failed - deployment monitoring unsuccessful")
    return False

if __name__ == "__main__":
    success = monitor_deployment()
    if success:
        print("\n🎉 DEPLOYMENT SUCCESSFUL - SYSTEM IS WORKING!")
    else:
        print("\n❌ DEPLOYMENT FAILED - MANUAL INTERVENTION REQUIRED")