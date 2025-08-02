#!/usr/bin/env python3
"""
Configure Paradigm ERP to send webhooks to our local service
"""

import requests
import json
import socket
import sys
from datetime import datetime

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        # Connect to an external server to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_auth_token():
    """Get a fresh auth token from Paradigm"""
    print("Getting auth token from Paradigm...")
    
    url = f"{config['paradigm']['api_base_url']}/user/Auth/GetToken"
    headers = {
        'accept': 'text/plain',
        'Authorization': config['paradigm']['bearer_token'],
        'x-api-key': config['paradigm']['api_key'],
        'Content-Type': 'application/json'
    }
    
    # Try both username formats
    usernames = [config['paradigm']['username'], f"{config['paradigm']['username']}@greenfieldmetalsales.com"]
    
    for username in usernames:
        print(f"  Trying: {username}")
        data = {
            'userName': username,
            'password': config['paradigm']['password']
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('isLoginValid', False):
                    token = response_data.get('data', '')
                    print(f"✓ Got new auth token with {username}")
                    print(f"✓ Token: {token[:50]}...")
                    return token
                else:
                    print(f"  Login invalid: {response_data.get('data', 'Unknown error')}")
            else:
                print(f"  Failed: {response.status_code}")
        except Exception as e:
            print(f"  Error: {str(e)}")
    
    print("✗ Failed to get token with both username formats")
    return None

def configure_webhook(webhook_url, auth_token=None):
    """Configure the webhook in Paradigm"""
    print(f"\nConfiguring webhook to: {webhook_url}")
    
    # Use provided token or the one from config
    token = auth_token or config['paradigm']['bearer_token']
    
    url = f"{config['paradigm']['api_base_url']}/Webhook"
    headers = {
        'accept': '*/*',
        'Authorization': token,
        'x-api-key': config['paradigm']['api_key'],
        'Content-Type': 'application/json'
    }
    
    # Configure webhook for order operations
    webhook_configs = [
        {
            "address": webhook_url,
            "dataOperation": "Create",
            "dataType": "SalesOrder",
            "httpType": "POST"
        },
        {
            "address": webhook_url,
            "dataOperation": "Update", 
            "dataType": "SalesOrder",
            "httpType": "POST"
        },
        {
            "address": webhook_url,
            "dataOperation": "Create",
            "dataType": "Invoice",
            "httpType": "POST"
        }
    ]
    
    success_count = 0
    for webhook_config in webhook_configs:
        print(f"  - Setting up {webhook_config['dataType']} {webhook_config['dataOperation']}...")
        try:
            response = requests.post(url, headers=headers, json=webhook_config)
            if response.status_code in [200, 201]:
                print(f"    ✓ Success")
                success_count += 1
            else:
                print(f"    ✗ Failed: {response.status_code}")
                print(f"    Response: {response.text}")
        except Exception as e:
            print(f"    ✗ Error: {str(e)}")
    
    return success_count == len(webhook_configs)

def test_webhook_connectivity(webhook_url):
    """Test if the webhook URL is accessible"""
    print(f"\nTesting connectivity to: {webhook_url}")
    
    try:
        # Extract just the base URL for health check
        base_url = webhook_url.replace('/paradigm-webhook', '/health')
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✓ Webhook service is accessible")
            return True
        else:
            print(f"✗ Service returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Cannot reach webhook service: {str(e)}")
        return False

def main():
    print("="*60)
    print("PARADIGM WEBHOOK CONFIGURATION")
    print("="*60)
    
    # Get local IP
    local_ip = get_local_ip()
    webhook_url = f"http://{local_ip}:{config['webhook']['port']}/paradigm-webhook"
    
    print(f"Local IP: {local_ip}")
    print(f"Webhook URL: {webhook_url}")
    
    # Test local service first
    if not test_webhook_connectivity(webhook_url):
        print("\n⚠️  WARNING: Webhook service is not running!")
        print("Start the service first with:")
        print("  python webhook_simple_print.py")
        print("or")
        print("  python main_app.py")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Get fresh auth token (optional)
    print("\nDo you want to get a fresh auth token? (y/n): ", end='')
    if input().lower() == 'y':
        new_token = get_auth_token()
        if new_token:
            # Update config with new token
            config['paradigm']['bearer_token'] = new_token
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=2)
            print("✓ Config updated with new token")
    
    # Configure webhook
    if configure_webhook(webhook_url):
        print("\n✅ WEBHOOK CONFIGURATION COMPLETE!")
        print(f"\nParadigm will now send webhooks to:")
        print(f"  {webhook_url}")
        print("\nNext steps:")
        print("1. Create an order in Paradigm")
        print("2. Check the logs:")
        print(f"   Get-Content 'C:\\BarTenderIntegration\\Logs\\webhook_{datetime.now().strftime('%Y%m%d')}.log' -Tail 20")
    else:
        print("\n❌ WEBHOOK CONFIGURATION FAILED!")
        print("Check the error messages above")

if __name__ == "__main__":
    main() 