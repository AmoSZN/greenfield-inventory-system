#!/usr/bin/env python3
"""
COMPREHENSIVE TEST SUITE - NO EXCUSES
This must pass 100% before any deployment
"""

import httpx
import asyncio
import json
import time
from datetime import datetime

# Test Configuration
LIVE_URL = "https://greenfield-inventory-system.onrender.com"
PARADIGM_BASE_URL = "https://greenfieldapi.para-apps.com"
PARADIGM_API_KEY = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
PARADIGM_USERNAME = "web_admin"
PARADIGM_PASSWORD = "ChangeMe#123!"

class ProductionReadinessTest:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def test_result(self, test_name: str, passed: bool, details: str = ""):
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        
        print(result)
        self.results.append(result)
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
            
        return passed
    
    async def test_direct_paradigm_api(self):
        """Test Paradigm API directly - MUST WORK"""
        print("\n🔥 TESTING PARADIGM API DIRECTLY...")
        
        try:
            auth_data = {"username": PARADIGM_USERNAME, "password": PARADIGM_PASSWORD}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test authentication
                response = await client.post(
                    f"{PARADIGM_BASE_URL}/api/user/Auth/GetToken",
                    json=auth_data,
                    headers={"X-API-Key": PARADIGM_API_KEY, "Content-Type": "application/json"}
                )
                
                auth_pass = self.test_result(
                    "Paradigm Authentication", 
                    response.status_code == 200,
                    f"Status: {response.status_code}"
                )
                
                if not auth_pass:
                    return False
                
                data = response.json()
                token = data.get("data")
                
                token_pass = self.test_result(
                    "Paradigm Token Retrieval",
                    token is not None,
                    f"Token length: {len(token) if token else 0}"
                )
                
                if not token_pass:
                    return False
                
                # Test GetItems
                headers = {"Authorization": f"Bearer {token}", "X-API-Key": PARADIGM_API_KEY}
                items_response = await client.get(
                    f"{PARADIGM_BASE_URL}/api/Items/GetItems/0/100",
                    headers=headers
                )
                
                items_pass = self.test_result(
                    "Paradigm GetItems",
                    items_response.status_code == 200,
                    f"Status: {items_response.status_code}"
                )
                
                if items_pass:
                    items = items_response.json()
                    self.test_result(
                        "Paradigm Data Quality",
                        isinstance(items, list) and len(items) > 0,
                        f"Items retrieved: {len(items) if isinstance(items, list) else 0}"
                    )
                
                return auth_pass and token_pass and items_pass
                
        except Exception as e:
            self.test_result("Paradigm API Connection", False, str(e))
            return False
    
    async def test_live_system_health(self):
        """Test live system health - MUST BE ONLINE"""
        print("\n🔥 TESTING LIVE SYSTEM HEALTH...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{LIVE_URL}/health")
                
                health_pass = self.test_result(
                    "System Health Check",
                    response.status_code == 200,
                    f"Status: {response.status_code}"
                )
                
                if health_pass:
                    data = response.json()
                    self.test_result(
                        "System Version",
                        data.get("version") == "2.5",
                        f"Version: {data.get('version')}"
                    )
                
                return health_pass
                
        except Exception as e:
            self.test_result("System Health", False, str(e))
            return False
    
    async def test_live_system_auth(self):
        """Test live system authentication - MUST WORK"""
        print("\n🔥 TESTING LIVE SYSTEM AUTHENTICATION...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{LIVE_URL}/api/paradigm/auth")
                
                auth_pass = self.test_result(
                    "Live System Auth Endpoint",
                    response.status_code == 200,
                    f"Status: {response.status_code}"
                )
                
                if auth_pass:
                    data = response.json()
                    self.test_result(
                        "Live System Authentication Success",
                        data.get("success") == True,
                        f"Success: {data.get('success')}, Authenticated: {data.get('authenticated')}"
                    )
                
                return auth_pass
                
        except Exception as e:
            self.test_result("Live System Auth", False, str(e))
            return False
    
    async def test_live_system_get_items(self):
        """Test live system get items - MUST RETURN DATA"""
        print("\n🔥 TESTING LIVE SYSTEM GET ITEMS...")
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(f"{LIVE_URL}/api/paradigm/items?skip=0&take=100")
                
                items_pass = self.test_result(
                    "Live System Get Items Endpoint",
                    response.status_code == 200,
                    f"Status: {response.status_code}"
                )
                
                if items_pass:
                    data = response.json()
                    
                    no_error = self.test_result(
                        "Live System No Errors",
                        "error" not in data or not data.get("error"),
                        f"Error: {data.get('error', 'None')}"
                    )
                    
                    has_data = self.test_result(
                        "Live System Has Data",
                        data.get("success") == True and len(data.get("items", [])) > 0,
                        f"Items count: {len(data.get('items', []))}"
                    )
                    
                    return items_pass and no_error and has_data
                
                return False
                
        except Exception as e:
            self.test_result("Live System Get Items", False, str(e))
            return False
    
    async def test_live_system_search(self):
        """Test live system search - MUST BE FAST"""
        print("\n🔥 TESTING LIVE SYSTEM SEARCH...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                start_time = time.time()
                response = await client.get(f"{LIVE_URL}/api/search?q=COIL")
                end_time = time.time()
                
                search_pass = self.test_result(
                    "Live System Search Endpoint",
                    response.status_code == 200,
                    f"Status: {response.status_code}"
                )
                
                speed_pass = self.test_result(
                    "Live System Search Speed",
                    (end_time - start_time) < 5.0,
                    f"Response time: {end_time - start_time:.2f}s"
                )
                
                if search_pass:
                    data = response.json()
                    results_pass = self.test_result(
                        "Live System Search Results",
                        data.get("success") == True,
                        f"Results: {len(data.get('items', []))}"
                    )
                    
                    return search_pass and speed_pass and results_pass
                
                return False
                
        except Exception as e:
            self.test_result("Live System Search", False, str(e))
            return False
    
    async def test_live_system_stats(self):
        """Test live system stats - MUST SHOW DATA"""
        print("\n🔥 TESTING LIVE SYSTEM STATS...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{LIVE_URL}/api/stats")
                
                stats_pass = self.test_result(
                    "Live System Stats Endpoint",
                    response.status_code == 200,
                    f"Status: {response.status_code}"
                )
                
                if stats_pass:
                    data = response.json()
                    
                    has_items = self.test_result(
                        "Live System Has Items in DB",
                        data.get("total_items", 0) > 0,
                        f"Total items: {data.get('total_items', 0)}"
                    )
                    
                    is_connected = self.test_result(
                        "Live System Paradigm Connected",
                        data.get("paradigm_connected") == True,
                        f"Connected: {data.get('paradigm_connected')}"
                    )
                    
                    return stats_pass and has_items and is_connected
                
                return False
                
        except Exception as e:
            self.test_result("Live System Stats", False, str(e))
            return False
    
    async def run_all_tests(self):
        """Run all tests - MUST PASS 100%"""
        print("🔥🔥🔥 COMPREHENSIVE PRODUCTION READINESS TEST 🔥🔥🔥")
        print("=" * 60)
        print("NO EXCUSES - SYSTEM MUST WORK 100%")
        print("=" * 60)
        
        # Test Paradigm API directly first
        paradigm_works = await self.test_direct_paradigm_api()
        
        # Test live system
        health_works = await self.test_live_system_health()
        auth_works = await self.test_live_system_auth()
        items_works = await self.test_live_system_get_items()
        search_works = await self.test_live_system_search()
        stats_works = await self.test_live_system_stats()
        
        # Final Results
        print("\n" + "=" * 60)
        print("🔥 FINAL RESULTS 🔥")
        print("=" * 60)
        
        for result in self.results:
            print(result)
        
        print(f"\n📊 SCORE: {self.passed}/{self.passed + self.failed} tests passed")
        
        if self.failed == 0:
            print("🎉 SYSTEM IS PRODUCTION READY!")
            return True
        else:
            print("❌ SYSTEM FAILED - NOT PRODUCTION READY")
            print("🔥 FIX ALL ISSUES BEFORE DEPLOYMENT")
            return False

async def main():
    tester = ProductionReadinessTest()
    is_ready = await tester.run_all_tests()
    
    if not is_ready:
        print("\n🚨 EMERGENCY ACTION REQUIRED 🚨")
        print("1. Fix all failed tests")
        print("2. Re-run this test suite")
        print("3. Only deploy when 100% pass rate achieved")
    
    return is_ready

if __name__ == "__main__":
    asyncio.run(main())
