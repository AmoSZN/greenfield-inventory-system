#!/usr/bin/env python3
"""
Test Paradigm ERP Update API directly
"""

import requests
import json
from datetime import datetime

# Paradigm Configuration
PARADIGM_BASE_URL = "https://greenfieldapi.para-apps.com"
PARADIGM_API_KEY = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
PARADIGM_USERNAME = "web_admin"
PARADIGM_PASSWORD = "ChangeMe#123!"

print("🧪 Testing Direct Paradigm Update")
print("=" * 60)

# Step 1: Authenticate
print("\n1️⃣ Authenticating...")
auth_response = requests.post(
    f"{PARADIGM_BASE_URL}/api/user/Auth/GetToken",
    headers={"x-api-key": PARADIGM_API_KEY},
    json={
        "userName": PARADIGM_USERNAME,
        "password": PARADIGM_PASSWORD
    }
)

if auth_response.status_code == 200:
    auth_data = auth_response.json()
    if auth_data.get("isLoginValid"):
        token = auth_data.get("data")
        print("✅ Authentication successful!")
    else:
        print("❌ Login invalid!")
        exit(1)
else:
    print(f"❌ Auth failed: {auth_response.status_code}")
    exit(1)

# Step 2: Test update for 1015B
print("\n2️⃣ Testing update for product 1015B...")

# First, let's get the current data
print("   Getting current data...")
try:
    current_response = requests.get(
        f"{PARADIGM_BASE_URL}/api/Items/GetItem/1015B",
        headers={
            "Authorization": f"Bearer {token}",
            "x-api-key": PARADIGM_API_KEY
        }
    )
    if current_response.status_code == 200:
        current_data = current_response.json()
        print(f"   Current quantity: {current_data.get('decUnitsInStock', 'Unknown')}")
    else:
        print(f"   ❌ Failed to get current data: {current_response.status_code}")
        print(f"   Response: {current_response.text}")
except Exception as e:
    print(f"   ❌ Error getting data: {e}")

# Now try to update
print("   Attempting update to 1000 units...")

update_payload = {
    "strProductID": "1015B",
    "decUnitsInStock": 1000.0,
    "dtmLastModified": datetime.now().isoformat()
}

headers = {
    "Authorization": f"Bearer {token}",
    "x-api-key": PARADIGM_API_KEY,
    "Content-Type": "application/json"
}

try:
    response = requests.put(
        f"{PARADIGM_BASE_URL}/api/Items/UpdateItem?excludeNullValues=true",
        headers=headers,
        json=update_payload,
        timeout=30
    )
    
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {response.text}")
    
    if response.status_code == 200:
        print("   ✅ Update successful!")
        
        # Verify the update
        print("   Verifying update...")
        verify_response = requests.get(
            f"{PARADIGM_BASE_URL}/api/Items/GetItem/1015B",
            headers={
                "Authorization": f"Bearer {token}",
                "x-api-key": PARADIGM_API_KEY
            }
        )
        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            print(f"   New quantity: {verify_data.get('decUnitsInStock', 'Unknown')}")
        else:
            print(f"   ❌ Verification failed: {verify_response.status_code}")
    else:
        print("   ❌ Update failed!")
        
except Exception as e:
    print(f"   ❌ Update error: {e}")

print("\n" + "=" * 60)
print("📝 Analysis:")
print("If this test works, the issue is in our inventory system.")
print("If this test fails, there's an issue with the Paradigm API call.")