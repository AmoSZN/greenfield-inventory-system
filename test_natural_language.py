#!/usr/bin/env python3
"""
Test Natural Language Processing
"""

import requests
import json

def test_natural_language():
    """Test the natural language endpoint"""
    
    print("🧪 Testing Natural Language Processing")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    test_commands = [
        "Add 50 units to product 1015B",
        "Set description for 1015B to Updated via Natural Language",
        "Update 1020B quantity to 200",
        "Increase inventory for 1025AW by 100 units"
    ]
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n{i}️⃣ Testing: {command}")
        
        try:
            response = requests.post(
                f"{base_url}/api/natural",
                json={"command": command},
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success: {result.get('success')}")
                print(f"   📝 Data: {result.get('data')}")
                if 'parsed' in result:
                    parsed = result['parsed']
                    print(f"   🔍 Parsed Product: {parsed.get('product_id')}")
                    print(f"   🔍 Parsed Updates: {parsed.get('updates')}")
            else:
                print(f"   ❌ Failed: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection failed - is the system running?")
            break
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test error handling
    print(f"\n5️⃣ Testing Error Handling")
    
    error_tests = [
        {"command": ""},  # Empty command
        {"command": "Invalid command without product ID"},  # No product ID
        {},  # No command field
    ]
    
    for i, test_data in enumerate(error_tests, 1):
        try:
            response = requests.post(
                f"{base_url}/api/natural",
                json=test_data,
                timeout=10
            )
            
            print(f"   Error Test {i}: Status {response.status_code}")
            if response.status_code == 400:
                print("   ✅ Proper error handling")
            else:
                print("   ⚠️  Unexpected response")
                
        except Exception as e:
            print(f"   ❌ Test error: {e}")

if __name__ == "__main__":
    test_natural_language()