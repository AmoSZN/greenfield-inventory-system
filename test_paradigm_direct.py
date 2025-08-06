#!/usr/bin/env python3
"""
Direct test of Paradigm API credentials
"""

import httpx
import asyncio
import json

# Paradigm API Configuration
PARADIGM_BASE_URL = "https://greenfieldapi.para-apps.com"
PARADIGM_API_KEY = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
PARADIGM_USERNAME = "web_admin"
PARADIGM_PASSWORD = "ChangeMe#123!"

async def test_paradigm_direct():
    """Test Paradigm API directly"""
    print("🔐 Testing Paradigm API directly...")
    print(f"🔐 URL: {PARADIGM_BASE_URL}")
    print(f"🔐 Username: {PARADIGM_USERNAME}")
    print(f"🔐 API Key: {PARADIGM_API_KEY[:10]}...")
    
    try:
        auth_data = {
            "username": PARADIGM_USERNAME,
            "password": PARADIGM_PASSWORD
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("🔐 Attempting authentication...")
            
            response = await client.post(
                f"{PARADIGM_BASE_URL}/api/user/Auth/GetToken",
                json=auth_data,
                headers={"X-API-Key": PARADIGM_API_KEY, "Content-Type": "application/json"}
            )
            
            print(f"🔐 Response Status: {response.status_code}")
            print(f"🔐 Response Headers: {dict(response.headers)}")
            print(f"🔐 Response Text: {response.text}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"🔐 Response JSON: {json.dumps(data, indent=2)}")
                    
                    token = data.get("token") or data.get("access_token") or data.get("accessToken") or data.get("data")
                    if token:
                        print("✅ Authentication successful!")
                        print(f"🔐 Token: {token[:20]}...")
                        
                        # Test getting items
                        print("\n📦 Testing GetItems...")
                        headers = {
                            "Authorization": f"Bearer {token}",
                            "X-API-Key": PARADIGM_API_KEY
                        }
                        
                        items_response = await client.get(
                            f"{PARADIGM_BASE_URL}/api/Items/GetItems/0/10",
                            headers=headers
                        )
                        
                        print(f"📦 Items Response Status: {items_response.status_code}")
                        print(f"📦 Items Response: {items_response.text[:500]}...")
                        
                        if items_response.status_code == 200:
                            try:
                                items_data = items_response.json()
                                print(f"📦 Items count: {len(items_data) if isinstance(items_data, list) else 'Not a list'}")
                                if isinstance(items_data, list) and len(items_data) > 0:
                                    print(f"📦 First item: {json.dumps(items_data[0], indent=2)}")
                            except:
                                print("📦 Could not parse items as JSON")
                        
                    else:
                        print("❌ No token found in response")
                        
                except Exception as e:
                    print(f"❌ JSON parsing error: {e}")
            else:
                print(f"❌ Authentication failed with status {response.status_code}")
                
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_paradigm_direct())
