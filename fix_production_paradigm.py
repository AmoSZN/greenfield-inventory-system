#!/usr/bin/env python3
"""
Fix Production Paradigm Integration
"""

import httpx
import asyncio
import json
import os

# Paradigm Configuration
PARADIGM_BASE_URL = "https://greenfieldapi.para-apps.com"
PARADIGM_API_KEY = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
PARADIGM_USERNAME = "web_admin"
PARADIGM_PASSWORD = "ChangeMe#123!"

async def test_paradigm_connection():
    """Test Paradigm API connection and find correct endpoints"""
    
    print("🔍 Testing Paradigm API connection...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Test authentication
            print("1. Testing authentication...")
            auth_data = {
                "username": PARADIGM_USERNAME,
                "password": PARADIGM_PASSWORD
            }
            
            auth_response = await client.post(
                f"{PARADIGM_BASE_URL}/api/user/Auth/GetToken",
                json=auth_data,
                headers={"X-API-Key": PARADIGM_API_KEY}
            )
            
            if auth_response.status_code == 200:
                token = auth_response.json().get("token")
                print(f"✅ Authentication successful! Token: {token[:20]}...")
                
                # Test different inventory endpoints
                headers = {
                    "Authorization": f"Bearer {token}",
                    "X-API-Key": PARADIGM_API_KEY
                }
                
                endpoints_to_test = [
                    "/api/Items/GetItems",
                    "/api/Inventory/GetItems", 
                    "/api/Products/GetAll",
                    "/api/Inventory/GetInventory",
                    "/api/Items/GetInventory",
                    "/api/Products/GetItems"
                ]
                
                print("\n2. Testing inventory endpoints...")
                for endpoint in endpoints_to_test:
                    try:
                        response = await client.get(
                            f"{PARADIGM_BASE_URL}{endpoint}",
                            headers=headers
                        )
                        print(f"   {endpoint}: {response.status_code}")
                        if response.status_code == 200:
                            data = response.json()
                            print(f"   ✅ SUCCESS! Found {len(data) if isinstance(data, list) else 'data'} items")
                            return endpoint, token
                    except Exception as e:
                        print(f"   {endpoint}: Error - {e}")
                
                print("\n❌ No working inventory endpoint found")
                return None, token
                
            else:
                print(f"❌ Authentication failed: {auth_response.status_code}")
                return None, None
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return None, None

async def update_production_app():
    """Update production app with correct endpoints"""
    
    print("\n🔧 Updating production app...")
    
    # Read current production app
    with open("production_app.py", "r") as f:
        content = f.read()
    
    # Update the inventory endpoint
    content = content.replace(
        'f"{PARADIGM_BASE_URL}/api/Items/GetItems"',
        'f"{PARADIGM_BASE_URL}/api/Inventory/GetItems"'  # Try this endpoint first
    )
    
    # Write updated content
    with open("production_app.py", "w") as f:
        f.write(content)
    
    print("✅ Production app updated")

async def test_webhook_setup():
    """Test webhook setup for Paradigm"""
    
    print("\n🔗 Testing webhook setup...")
    
    webhook_url = "https://greenfield-inventory-system.onrender.com/paradigm-webhook"
    
    print(f"Webhook URL: {webhook_url}")
    print("\nTo configure Paradigm webhook:")
    print("1. Log into Paradigm ERP")
    print("2. Go to System Settings > Webhooks")
    print(f"3. Add webhook URL: {webhook_url}")
    print("4. Set events: Inventory Update, Item Modified")
    print("5. Test the webhook")

async def main():
    """Main function to fix production system"""
    
    print("🚀 FIXING PRODUCTION PARADIGM INTEGRATION")
    print("=" * 50)
    
    # Test Paradigm connection
    endpoint, token = await test_paradigm_connection()
    
    if endpoint:
        print(f"\n✅ Found working endpoint: {endpoint}")
        await update_production_app()
    else:
        print("\n❌ Could not find working inventory endpoint")
        print("Please check Paradigm API documentation")
    
    # Test webhook setup
    await test_webhook_setup()
    
    print("\n" + "=" * 50)
    print("🎯 NEXT STEPS:")
    print("1. Deploy updated production_app.py to Render")
    print("2. Configure Paradigm webhook")
    print("3. Test live inventory updates")
    print("4. Access: https://greenfield-inventory-system.onrender.com")

if __name__ == "__main__":
    asyncio.run(main())
