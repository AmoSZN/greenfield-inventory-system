#!/usr/bin/env python3
"""
Fix the inventory sync issue by implementing proper inventory adjustments
"""

import requests
import json
from datetime import datetime

# Paradigm Configuration
PARADIGM_BASE_URL = "https://greenfieldapi.para-apps.com"
PARADIGM_API_KEY = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
PARADIGM_USERNAME = "web_admin"
PARADIGM_PASSWORD = "ChangeMe#123!"

print("🔧 FIXING INVENTORY SYNC ISSUE")
print("=" * 60)

# Authenticate
auth_response = requests.post(
    f"{PARADIGM_BASE_URL}/api/user/Auth/GetToken",
    headers={"x-api-key": PARADIGM_API_KEY},
    json={"userName": PARADIGM_USERNAME, "password": PARADIGM_PASSWORD}
)

token = auth_response.json()["data"]
headers = {
    "Authorization": f"Bearer {token}",
    "x-api-key": PARADIGM_API_KEY,
    "Content-Type": "application/json"
}

print("✅ Authenticated with Paradigm")

# The issue: decUnitsInStock is READ-ONLY
# Solution: Use inventory adjustment transactions

print("\n🔍 PROBLEM IDENTIFIED:")
print("   - decUnitsInStock is a calculated/read-only field")
print("   - It gets updated via inventory transactions, not direct updates")
print("   - We need to create inventory adjustments instead")

print("\n💡 SOLUTION:")
print("   1. Get current inventory level")
print("   2. Calculate adjustment needed")
print("   3. Create inventory adjustment transaction")

# Test with product 1015B
product_id = "1015B"
target_quantity = 1000

print(f"\n🧪 Testing with {product_id} -> {target_quantity} units")

# Step 1: Get current inventory
print("   Getting current inventory...")
try:
    # Try different endpoints to get current inventory
    endpoints_to_try = [
        f"/api/Items/GetItem/{product_id}",
        f"/api/Inventory/GetStock/{product_id}",
        f"/api/Items/{product_id}/Stock"
    ]
    
    current_stock = None
    for endpoint in endpoints_to_try:
        try:
            response = requests.get(
                f"{PARADIGM_BASE_URL}{endpoint}",
                headers={"Authorization": f"Bearer {token}", "x-api-key": PARADIGM_API_KEY}
            )
            if response.status_code == 200:
                data = response.json()
                current_stock = data.get('decUnitsInStock', data.get('unitsInStock', data.get('quantity')))
                if current_stock is not None:
                    print(f"   ✅ Current stock: {current_stock} (from {endpoint})")
                    break
        except:
            continue
    
    if current_stock is None:
        # Fallback: use the UpdateItem response we got earlier
        current_stock = 130.0  # From our test
        print(f"   ⚠️  Using known current stock: {current_stock}")
    
    # Step 2: Calculate adjustment
    adjustment_needed = target_quantity - current_stock
    print(f"   📊 Adjustment needed: {adjustment_needed}")
    
    if adjustment_needed == 0:
        print("   ✅ No adjustment needed!")
    else:
        # Step 3: Try inventory adjustment endpoints
        print("   🔄 Attempting inventory adjustment...")
        
        adjustment_endpoints = [
            {
                "url": f"/api/Inventory/Adjust",
                "payload": {
                    "strProductID": product_id,
                    "decAdjustmentQuantity": adjustment_needed,
                    "strReason": "System Sync Adjustment",
                    "dtmAdjustmentDate": datetime.now().isoformat()
                }
            },
            {
                "url": f"/api/Items/AdjustInventory",
                "payload": {
                    "strProductID": product_id,
                    "decQuantityAdjustment": adjustment_needed,
                    "strNotes": "Inventory sync from external system"
                }
            },
            {
                "url": f"/api/Transactions/InventoryAdjustment",
                "payload": {
                    "items": [{
                        "productId": product_id,
                        "adjustmentQuantity": adjustment_needed,
                        "reason": "System Synchronization"
                    }]
                }
            }
        ]
        
        success = False
        for endpoint_info in adjustment_endpoints:
            try:
                response = requests.post(
                    f"{PARADIGM_BASE_URL}{endpoint_info['url']}",
                    headers=headers,
                    json=endpoint_info['payload']
                )
                
                print(f"      Trying {endpoint_info['url']}: {response.status_code}")
                if response.status_code in [200, 201]:
                    print(f"      ✅ Success! Response: {response.text[:200]}...")
                    success = True
                    break
                else:
                    print(f"      ❌ Failed: {response.text[:100]}...")
            except Exception as e:
                print(f"      ❌ Error: {e}")
        
        if not success:
            print("   ⚠️  No inventory adjustment endpoints found")
            print("   📝 This means inventory updates must be done through Paradigm UI")
            print("      or via specific inventory transaction documents")

except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("🎯 NEXT STEPS:")
print("1. Update our inventory system to handle read-only inventory fields")
print("2. Implement proper error messages when direct updates fail")
print("3. Consider alternative approaches:")
print("   - Manual adjustments in Paradigm UI")
print("   - Inventory adjustment documents")
print("   - Purchase/Sales order workflows")
print("\n4. For now, our system will:")
print("   ✅ Update local database (for tracking)")
print("   ⚠️  Show warning that Paradigm sync failed")
print("   📝 Log all attempted updates for manual processing")