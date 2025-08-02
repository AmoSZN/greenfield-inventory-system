#!/usr/bin/env python3
"""
Simple authentication test for Paradigm ERP
"""

import requests

# Paradigm ERP Configuration
PARADIGM_BASE_URL = "https://greenfieldapi.para-apps.com"
PARADIGM_API_KEY = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
PARADIGM_USERNAME = "web_admin"
PARADIGM_PASSWORD = "ChangeMe#123!"

print("Testing Paradigm ERP Authentication...")
print("=" * 50)

try:
    # Test authentication
    response = requests.post(
        f"{PARADIGM_BASE_URL}/api/Authenticate",
        json={
            "strUserName": PARADIGM_USERNAME,
            "strPassword": PARADIGM_PASSWORD
        },
        headers={"x-api-key": PARADIGM_API_KEY}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("data", {}).get("token")
        if token:
            print(f"\n✅ Authentication successful!")
            print(f"Token (first 50 chars): {token[:50]}...")
        else:
            print("\n❌ No token in response")
    else:
        print(f"\n❌ Authentication failed with status {response.status_code}")
        
except Exception as e:
    print(f"\n❌ Error: {str(e)}")

print("\nTesting connection to inventory system...")
try:
    inv_response = requests.get("http://localhost:8000/api/stats")
    if inv_response.status_code == 200:
        stats = inv_response.json()
        print(f"✅ Inventory system connected")
        print(f"   Products in database: {stats.get('total_products', 0)}")
    else:
        print(f"❌ Inventory system returned {inv_response.status_code}")
except:
    print("❌ Cannot connect to inventory system")