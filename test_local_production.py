#!/usr/bin/env python3
"""
Test the production app locally before deployment
"""

import asyncio
import httpx
import sys

async def test_local():
    """Test local production system"""
    print("🔍 Testing Local Production System")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        tests = [
            ("/health", "Health Check"),
            ("/api/stats", "API Stats"),
            ("/test-webhook", "Webhook Test"),
        ]
        
        passed = 0
        failed = 0
        
        for endpoint, description in tests:
            try:
                response = await client.get(f"{base_url}{endpoint}")
                if response.status_code == 200:
                    print(f"✅ {description}: PASS")
                    passed += 1
                else:
                    print(f"❌ {description}: FAIL (Status: {response.status_code})")
                    failed += 1
            except Exception as e:
                print(f"❌ {description}: ERROR - {e}")
                failed += 1
        
        print("\n" + "=" * 50)
        print(f"Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("✅ Local system ready for deployment!")
            return True
        else:
            print("❌ Local system has issues")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_local())
    sys.exit(0 if success else 1)
