#!/usr/bin/env python3
"""
Test Paradigm authentication with different username/password combinations
"""

import requests
import json

print("PARADIGM AUTHENTICATION TEST")
print("="*50)

# API configuration
api_base_url = "https://greenfieldapi.para-apps.com/api"
api_key = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
bearer_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJVc2VyTmFtZSI6IldlYl9BZG1pbiIsIlN0clBhcmFkaWdtVXNlciI6IldlYl9BZG1pbiIsIlN0ckZpcnN0TmFtZSI6IldlYiIsIlN0ckxhc3ROYW1lIjoiQWRtaW4iLCJleHAiOjE3NTI4Mjk3NDAsImlzcyI6IlBhcmFkaWdtIiwiYXVkIjoiUGFyYWRpZ20ifQ.hO_49X_jO5AKQmHz468jp80j6jYlZ8HNLLi8P2qwQUM"

# Get credentials from user
print("\nCurrent credentials in config:")
print("  Username: mattamundson")
print("  Password: Morrison216!")
print("")

use_custom = input("Do you want to test different credentials? (y/n): ")

if use_custom.lower() == 'y':
    username = input("Enter username: ")
    password = input("Enter password: ")
else:
    username = "mattamundson"
    password = "Morrison216!"

# Test both username formats
usernames_to_test = [username]
if '@' not in username:
    usernames_to_test.append(f"{username}@greenfieldmetalsales.com")

print("\nTesting authentication...")
print("-"*50)

url = f"{api_base_url}/user/Auth/GetToken"
headers = {
    'accept': 'text/plain',
    'Authorization': bearer_token,
    'x-api-key': api_key,
    'Content-Type': 'application/json'
}

success = False
for test_username in usernames_to_test:
    print(f"\nTesting: {test_username}")
    
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
                token = result.get('data', '')
                print(f"\n✅ SUCCESS! Valid credentials: {test_username}")
                print(f"Token: {token[:50]}...")
                
                # Update config.json
                update = input("\nUpdate config.json with these credentials? (y/n): ")
                if update.lower() == 'y':
                    with open('config.json', 'r') as f:
                        config = json.load(f)
                    
                    config['paradigm']['username'] = test_username
                    config['paradigm']['password'] = password
                    if token:
                        config['paradigm']['bearer_token'] = token
                    
                    with open('config.json', 'w') as f:
                        json.dump(config, f, indent=2)
                    
                    print("✓ Config updated!")
                
                success = True
                break
            else:
                print(f"  ❌ Login failed: {result.get('data', 'Unknown error')}")
        else:
            print(f"  ❌ HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")

if not success:
    print("\n❌ Authentication failed with all attempts")
    print("\nPossible issues:")
    print("1. Incorrect username or password")
    print("2. Account locked or disabled")
    print("3. API token expired (though it responded)")
    print("\nPlease verify your Paradigm credentials")
else:
    print("\n✅ Authentication successful!")
    print("Next steps:")
    print("1. Run: .\\QUICK_START.ps1")
    print("2. Choose option 2 to configure webhook")
    print("3. Set up external access (see EXTERNAL_ACCESS_GUIDE.md)") 