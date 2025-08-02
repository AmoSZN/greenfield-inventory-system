#!/usr/bin/env python3
"""
Test different inventory fields for updating
"""

import requests
import json
from datetime import datetime

# Paradigm Configuration
PARADIGM_BASE_URL = "https://greenfieldapi.para-apps.com"
PARADIGM_API_KEY = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
PARADIGM_USERNAME = "web_admin"
PARADIGM_PASSWORD = "ChangeMe#123!"

print("🔬 Testing Different Inventory Fields")
print("=" * 60)

# Authenticate
auth_response = requests.post(
    f"{PARADIGM_BASE_URL}/api/user/Auth/GetToken",
    headers={"x-api-key": PARADIGM_API_KEY},
    json={"userName": PARADIGM_USERNAME, "password": PARADIGM_PASSWORD}
)

token = auth_response.json()["data"]
print("✅ Authenticated")

headers = {
    "Authorization": f"Bearer {token}",
    "x-api-key": PARADIGM_API_KEY,
    "Content-Type": "application/json"
}

# Test different field combinations
test_cases = [
    {
        "name": "Test 1: decUnitsInStock only",
        "payload": {
            "strProductID": "1015B",
            "decUnitsInStock": 1000.0
        }
    },
    {
        "name": "Test 2: Add dtmLastModified",
        "payload": {
            "strProductID": "1015B",
            "decUnitsInStock": 1000.0,
            "dtmLastModified": datetime.now().isoformat()
        }
    },
    {
        "name": "Test 3: Use inventory adjustment approach",
        "payload": {
            "strProductID": "1015B",
            "decUnitsInStock": 1000.0,
            "decUnitsReceived": 870.0,  # Difference to get to 1000
            "dtmLastModified": datetime.now().isoformat()
        }
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"\n{i}️⃣ {test['name']}")
    print(f"   Payload: {json.dumps(test['payload'], indent=2)}")
    
    try:
        response = requests.put(
            f"{PARADIGM_BASE_URL}/api/Items/UpdateItem?excludeNullValues=true",
            headers=headers,
            json=test['payload'],
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            current_stock = data.get('decUnitsInStock', 'Unknown')
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📦 Result Stock: {current_stock}")
            
            if current_stock == 1000.0:
                print("   🎉 SUCCESS! This method works!")
                break
            else:
                print("   ⚠️  Stock didn't change as expected")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("🔍 Let's check what Paradigm documentation says about inventory adjustments...")

# Try the inventory adjustment API if it exists
print("\n📝 Trying Inventory Adjustment API...")
adjustment_payload = {
    "strProductID": "1015B",
    "decAdjustmentQuantity": 870.0,  # To get from 130 to 1000
    "strReason": "System Update",
    "dtmAdjustmentDate": datetime.now().isoformat()
}

try:
    adj_response = requests.post(
        f"{PARADIGM_BASE_URL}/api/Inventory/Adjustment",
        headers=headers,
        json=adjustment_payload,
        timeout=30
    )
    print(f"Adjustment API Status: {adj_response.status_code}")
    print(f"Response: {adj_response.text}")
except Exception as e:
    print(f"Adjustment API Error: {e}")

print("\n🎯 RECOMMENDATION:")
print("If none of these work, we may need to use Paradigm's")
print("Inventory Adjustment feature through their UI or a different API endpoint.")