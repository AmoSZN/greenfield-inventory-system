#!/usr/bin/env python3
"""
Test script for the new Paradigm integration functionality
"""

import httpx
import asyncio
import json

BASE_URL = "https://greenfield-inventory-system.onrender.com"

async def test_all_functionality():
    """Test all new functionality"""
    print("🧪 TESTING NEW PARADIGM INTEGRATION FUNCTIONALITY")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Get ALL inventory items
        print("\n1️⃣ Testing: Get ALL Inventory Items")
        try:
            response = await client.get(f"{BASE_URL}/api/paradigm/items?skip=0&take=10000")
            data = response.json()
            if data.get("success"):
                print(f"✅ SUCCESS: Retrieved {data.get('count', 0)} items from Paradigm")
                if data.get('count', 0) > 10:
                    print(f"   ✅ Confirmed: Getting more than 10 items (was limited before)")
                else:
                    print(f"   ⚠️  WARNING: Only got {data.get('count', 0)} items - may still be limited")
            else:
                print(f"❌ FAILED: {data.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        # Test 2: Search functionality
        print("\n2️⃣ Testing: Search Products")
        try:
            response = await client.get(f"{BASE_URL}/api/paradigm/search?q=COIL")
            data = response.json()
            if data.get("success"):
                print(f"✅ SUCCESS: Found {data.get('count', 0)} items containing 'COIL'")
                if data.get('items'):
                    print(f"   📦 Sample items: {[item.get('product_id') for item in data['items'][:3]]}")
            else:
                print(f"❌ FAILED: {data.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        # Test 3: Update functionality with a real product
        print("\n3️⃣ Testing: Update Product Quantity")
        try:
            # First get items to find a real product ID
            items_response = await client.get(f"{BASE_URL}/api/paradigm/items?skip=0&take=10000")
            items_data = items_response.json()
            
            if items_data.get("success") and items_data.get("items"):
                # Find a product with a real ID
                real_product = None
                for item in items_data["items"]:
                    if item.get("strProductID") and len(item.get("strProductID", "")) > 3:
                        real_product = item.get("strProductID")
                        break
                
                if real_product:
                    print(f"   🔍 Testing update for product: {real_product}")
                    update_data = {"product_id": real_product, "quantity": 999}
                    response = await client.post(
                        f"{BASE_URL}/api/paradigm/update-quantity",
                        json=update_data,
                        headers={"Content-Type": "application/json"}
                    )
                    data = response.json()
                    if data.get("success"):
                        print(f"✅ SUCCESS: Updated {real_product} to quantity 999")
                    else:
                        print(f"❌ FAILED: {data.get('error', 'Unknown error')}")
                else:
                    print("❌ FAILED: Could not find a real product ID to test with")
            else:
                print("❌ FAILED: Could not get items to test update")
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        # Test 4: Sync functionality
        print("\n4️⃣ Testing: Sync to Local Database")
        try:
            response = await client.post(f"{BASE_URL}/api/paradigm/sync")
            data = response.json()
            if data.get("success"):
                print(f"✅ SUCCESS: Synced {data.get('items_synced', 0)} items to local database")
            else:
                print(f"❌ FAILED: {data.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_all_functionality())
