#!/usr/bin/env python3
"""
Configure Paradigm Webhooks for Real-time Inventory Sync
"""

import requests
import json
from datetime import datetime

# Paradigm Configuration
PARADIGM_BASE_URL = "https://greenfieldapi.para-apps.com"
PARADIGM_API_KEY = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
PARADIGM_USERNAME = "web_admin"
PARADIGM_PASSWORD = "ChangeMe#123!"

# Your ngrok webhook URL for public access
LOCAL_WEBHOOK_URL = "https://95891b50740f.ngrok-free.app/webhook/paradigm"

print("🔧 Configuring Paradigm Webhooks")
print("=" * 60)

# First, authenticate to get a fresh token
print("\n1️⃣ Authenticating with Paradigm...")
auth_response = requests.post(
    f"{PARADIGM_BASE_URL}/api/Authenticate",
    json={
        "userName": PARADIGM_USERNAME,
        "password": PARADIGM_PASSWORD
    },
    headers={"x-api-key": PARADIGM_API_KEY}
)

if auth_response.status_code == 200:
    auth_data = auth_response.json()
    auth_token = auth_data.get("data", {}).get("token")
    print("✅ Authentication successful")
else:
    print(f"❌ Authentication failed: {auth_response.status_code}")
    print(auth_response.text)
    exit(1)

# Configure webhooks for different events
webhooks_to_create = [
    {
        "name": "Inventory Update",
        "address": LOCAL_WEBHOOK_URL,
        "dataOperation": "UPDATE",
        "dataType": "INVENTORY",
        "httpType": "POST"
    },
    {
        "name": "Sales Order",
        "address": LOCAL_WEBHOOK_URL,
        "dataOperation": "CREATE",
        "dataType": "SALES_ORDER",
        "httpType": "POST"
    },
    {
        "name": "Purchase Order",
        "address": LOCAL_WEBHOOK_URL,
        "dataOperation": "CREATE",
        "dataType": "PURCHASE_ORDER",
        "httpType": "POST"
    },
    {
        "name": "Stock Adjustment",
        "address": LOCAL_WEBHOOK_URL,
        "dataOperation": "UPDATE",
        "dataType": "STOCK_ADJUSTMENT",
        "httpType": "POST"
    }
]

print("\n2️⃣ Creating webhooks...")
created_webhooks = []

for webhook in webhooks_to_create:
    print(f"\n   Creating webhook: {webhook['name']}")
    
    response = requests.post(
        f"{PARADIGM_BASE_URL}/api/Webhook",
        json={
            "address": webhook["address"],
            "dataOperation": webhook["dataOperation"],
            "dataType": webhook["dataType"],
            "httpType": webhook["httpType"]
        },
        headers={
            "Authorization": f"Bearer {auth_token}",
            "x-api-key": PARADIGM_API_KEY,
            "Content-Type": "application/json"
        }
    )
    
    if response.status_code in [200, 201]:
        print(f"   ✅ Created: {webhook['name']}")
        created_webhooks.append(webhook)
    else:
        print(f"   ❌ Failed: {response.status_code}")
        print(f"      Response: {response.text}")

print("\n" + "=" * 60)
print(f"📊 Summary:")
print(f"   Webhooks created: {len(created_webhooks)}/{len(webhooks_to_create)}")

if created_webhooks:
    print("\n✅ Webhook Configuration Complete!")
    print("\n⚠️  IMPORTANT: Your webhooks are pointing to localhost.")
    print("   To receive events from Paradigm cloud, you need a public URL.")
    print("\n   Options:")
    print("   1. Use ngrok: ngrok http 8000")
    print("   2. Deploy to Azure (recommended for production)")
    print("   3. Use port forwarding (if you have static IP)")
    
    print("\n📝 Next Steps:")
    print("   1. Set up public access (ngrok or Azure)")
    print("   2. Update webhook URLs in Paradigm")
    print("   3. Test with a real inventory change")
else:
    print("\n❌ No webhooks were created. Check the errors above.")

# Save webhook configuration
config = {
    "created_at": datetime.now().isoformat(),
    "webhooks": created_webhooks,
    "local_url": LOCAL_WEBHOOK_URL,
    "paradigm_base": PARADIGM_BASE_URL
}

with open('webhook_config.json', 'w') as f:
    json.dump(config, f, indent=2)

print(f"\n💾 Configuration saved to webhook_config.json")