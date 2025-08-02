#!/usr/bin/env python3
"""
Test the inventory fix - verify proper error messages
"""

import requests
import json

print("🧪 Testing Inventory Fix")
print("=" * 50)

# Test the updated system
base_url = "http://localhost:8000"

# Test 1: Update quantity (should be local only)
print("\n1️⃣ Testing quantity update (should be local only)...")
try:
    response = requests.post(
        f"{base_url}/api/update",
        json={
            "product_id": "1015B",
            "updates": {"quantity": 1000}
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   Status: {result.get('success')}")
        print(f"   Message: {result.get('data', result.get('error', 'No message'))}")
    else:
        print(f"   ❌ HTTP Error: {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Update description (should sync to Paradigm)
print("\n2️⃣ Testing description update (should sync to Paradigm)...")
try:
    response = requests.post(
        f"{base_url}/api/update",
        json={
            "product_id": "1015B",
            "updates": {"description": "Updated #10 Screws - 1.5\" - Metal to Wood - BLACK (Test Update)"}
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   Status: {result.get('success')}")
        print(f"   Message: {result.get('data', result.get('error', 'No message'))}")
    else:
        print(f"   ❌ HTTP Error: {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Update both (mixed local/Paradigm)
print("\n3️⃣ Testing mixed update (quantity + description)...")
try:
    response = requests.post(
        f"{base_url}/api/update",
        json={
            "product_id": "1015B",
            "updates": {
                "quantity": 1500,
                "description": "Updated #10 Screws - MIXED UPDATE TEST"
            }
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   Status: {result.get('success')}")
        print(f"   Message: {result.get('data', result.get('error', 'No message'))}")
    else:
        print(f"   ❌ HTTP Error: {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 50)
print("✅ Test complete!")
print("\n📝 Expected results:")
print("   1. Quantity updates: Local only with warning")
print("   2. Description updates: Sync to Paradigm")
print("   3. Mixed updates: Clear messages for each type")