#!/usr/bin/env python3
"""
Test Paradigm authentication with web_admin credentials
"""

import requests
import json

print("PARADIGM AUTHENTICATION TEST - web_admin")
print("="*50)

# API configuration (from existing file)
api_base_url = "https://greenfieldapi.para-apps.com/api"
api_key = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
bearer_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJVc2VyTmFtZSI6IldlYl9BZG1pbiIsIlN0clBhcmFkaWdtVXNlciI6IldlYl9BZG1pbiIsIlN0ckZpcnN0TmFtZSI6IldlYiIsIlN0ckxhc3ROYW1lIjoiQWRtaW4iLCJleHAiOjE3NTI4Mjk3NDAsImlzcyI6IlBhcmFkaWdtIiwiYXVkIjoiUGFyYWRpZ20ifQ.hO_49X_jO5AKQmHz468jp80j6jYlZ8HNLLi8P2qwQUM"

# New credentials
username = "web_admin"
password = "ChangeMe#123!"

# Test both username formats
usernames_to_test = [
    "web_admin",
    "Web_Admin",  # Case variation
    "web_admin@greenfieldmetalsales.com"
]

print(f"\nTesting credentials:")
print(f"  Password: {'*' * (len(password) - 4) + password[-4:]}")
print("\nTrying authentication...")
print("-"*50)

url = f"{api_base_url}/user/Auth/GetToken"
headers = {
    'accept': 'text/plain',
    'Authorization': bearer_token,
    'x-api-key': api_key,
    'Content-Type': 'application/json'
}

success = False
working_username = None
auth_token = None

for test_username in usernames_to_test:
    print(f"\nTesting username: {test_username}")
    
    data = {
        'userName': test_username,
        'password': password
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  Response: {json.dumps(result, indent=2)}")
            
            if result.get('isLoginValid', False):
                auth_token = result.get('data', '')
                print(f"\n✅ SUCCESS! Valid credentials: {test_username}")
                print(f"Token: {auth_token[:50]}...")
                working_username = test_username
                success = True
                break
            else:
                print(f"  ❌ Login failed: {result.get('data', 'Unknown error')}")
        else:
            print(f"  ❌ HTTP Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")

if success:
    print("\n" + "="*50)
    print("✅ AUTHENTICATION SUCCESSFUL!")
    print("="*50)
    print(f"\nWorking username: {working_username}")
    print(f"API endpoint: {api_base_url}")
    
    # Update config.json automatically
    print("\nUpdating config.json...")
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        config['paradigm']['username'] = working_username
        config['paradigm']['password'] = password
        if auth_token:
            config['paradigm']['bearer_token'] = auth_token
        
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Config.json updated successfully!")
        
    except Exception as e:
        print(f"❌ Error updating config: {e}")
    
    print("\n🚀 Next Steps:")
    print("1. Set up external access (ngrok or port forwarding)")
    print("2. Configure webhook URL in Paradigm")
    print("3. Test end-to-end order processing")
    
else:
    print("\n" + "="*50)
    print("❌ AUTHENTICATION FAILED")
    print("="*50)
    print("\nAll username variations failed. Please check:")
    print("1. Credentials are correct")
    print("2. Account is active and has API access")
    print("3. Contact Paradigm support if needed")
    
    # Also try to get more info about the API
    print("\nTrying to get API info without auth...")
    try:
        # Try health check or version endpoints
        test_endpoints = [
            f"{api_base_url}/health",
            f"{api_base_url}/version",
            f"{api_base_url}/",
            "https://greenfieldapi.para-apps.com/api/swagger"
        ]
        
        for endpoint in test_endpoints:
            try:
                resp = requests.get(endpoint, timeout=3)
                if resp.status_code < 500:
                    print(f"\n{endpoint} returned: {resp.status_code}")
                    if resp.text:
                        print(f"Content: {resp.text[:200]}")
            except:
                pass
                
    except:
        pass

print("\n✅ Test complete!")