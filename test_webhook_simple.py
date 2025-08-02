#!/usr/bin/env python3
"""
Simple webhook configuration test
"""

import requests
import json

# Your ngrok URL
NGROK_URL = "https://95891b50740f.ngrok-free.app"

print("🧪 Testing Webhook Configuration")
print("=" * 60)

# Test 1: Check if ngrok is accessible
print("\n1️⃣ Testing ngrok tunnel...")
try:
    response = requests.get(NGROK_URL, timeout=5)
    print(f"✅ Ngrok accessible: {response.status_code}")
except Exception as e:
    print(f"❌ Ngrok error: {e}")

# Test 2: Check webhook endpoint
print("\n2️⃣ Testing webhook endpoint...")
try:
    response = requests.get(f"{NGROK_URL}/webhook/paradigm", timeout=5)
    print(f"✅ Webhook endpoint: {response.status_code}")
except Exception as e:
    print(f"❌ Webhook error: {e}")

# Test 3: Send test webhook
print("\n3️⃣ Sending test webhook...")
test_payload = {
    "eventType": "INVENTORY_UPDATE",
    "productId": "1010AG",
    "quantity": 150,
    "timestamp": "2024-01-01T12:00:00Z"
}

try:
    response = requests.post(
        f"{NGROK_URL}/webhook/paradigm",
        json=test_payload,
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    print(f"✅ Test webhook sent: {response.status_code}")
    if response.text:
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"❌ Send error: {e}")

print("\n" + "=" * 60)
print("📝 Manual Webhook Setup:")
print(f"\n1. Use this webhook URL in Paradigm:")
print(f"   {NGROK_URL}/webhook/paradigm")
print("\n2. Configure for these events:")
print("   - Inventory Updates")
print("   - Sales Orders")
print("   - Purchase Orders")
print("   - Stock Adjustments")
print("\n3. Test with a real change in Paradigm")
print("\n✅ Your system is ready to receive webhooks!")