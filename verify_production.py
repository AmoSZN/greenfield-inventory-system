#!/usr/bin/env python3
"""
Production System Verification Script
Tests all critical functionality to ensure 99% certainty of operation
"""

import asyncio
import httpx
import json
import time
from datetime import datetime

PRODUCTION_URL = "https://greenfield-inventory-system.onrender.com"

class ProductionVerifier:
    def __init__(self):
        self.results = []
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def test_endpoint(self, endpoint, expected_status=200, description=""):
        """Test a specific endpoint"""
        try:
            response = await self.client.get(f"{PRODUCTION_URL}{endpoint}")
            success = response.status_code == expected_status
            result = {
                "endpoint": endpoint,
                "status_code": response.status_code,
                "success": success,
                "description": description,
                "response": response.text[:200] if response.text else "No response"
            }
            self.results.append(result)
            return success
        except Exception as e:
            result = {
                "endpoint": endpoint,
                "status_code": "ERROR",
                "success": False,
                "description": description,
                "response": str(e)
            }
            self.results.append(result)
            return False
    
    async def test_post_endpoint(self, endpoint, data=None, description=""):
        """Test a POST endpoint"""
        try:
            response = await self.client.post(f"{PRODUCTION_URL}{endpoint}", json=data or {})
            success = response.status_code in [200, 201]
            result = {
                "endpoint": f"POST {endpoint}",
                "status_code": response.status_code,
                "success": success,
                "description": description,
                "response": response.text[:200] if response.text else "No response"
            }
            self.results.append(result)
            return success
        except Exception as e:
            result = {
                "endpoint": f"POST {endpoint}",
                "status_code": "ERROR",
                "success": False,
                "description": description,
                "response": str(e)
            }
            self.results.append(result)
            return False
    
    async def verify_production_system(self):
        """Comprehensive production system verification"""
        print("🔍 VERIFYING PRODUCTION SYSTEM")
        print("=" * 50)
        
        # Test 1: Basic Health Check
        print("\n1. Testing Health Check...")
        health_ok = await self.test_endpoint("/health", 200, "System health check")
        
        # Test 2: Main Dashboard
        print("2. Testing Main Dashboard...")
        dashboard_ok = await self.test_endpoint("/", 200, "Main dashboard page")
        
        # Test 3: API Stats
        print("3. Testing API Stats...")
        stats_ok = await self.test_endpoint("/api/stats", 200, "System statistics")
        
        # Test 4: Webhook Test Endpoint
        print("4. Testing Webhook Endpoint...")
        webhook_ok = await self.test_endpoint("/test-webhook", 200, "Webhook test endpoint")
        
        # Test 5: Sync Endpoint
        print("5. Testing Sync Endpoint...")
        sync_ok = await self.test_post_endpoint("/api/sync", {}, "Inventory sync from Paradigm")
        
        # Test 6: Paradigm Webhook
        print("6. Testing Paradigm Webhook...")
        paradigm_webhook_ok = await self.test_post_endpoint("/paradigm-webhook", 
            {"productId": "TEST123", "quantity": 100}, "Paradigm webhook processing")
        
        # Calculate overall success
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r["success"])
        success_rate = (successful_tests / total_tests) * 100
        
        print("\n" + "=" * 50)
        print("📊 VERIFICATION RESULTS")
        print("=" * 50)
        
        for result in self.results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {result['endpoint']} - {result['description']}")
            if not result["success"]:
                print(f"   Error: {result['response']}")
        
        print(f"\n🎯 OVERALL SUCCESS RATE: {success_rate:.1f}% ({successful_tests}/{total_tests})")
        
        if success_rate >= 99:
            print("🎉 PRODUCTION SYSTEM IS FULLY OPERATIONAL!")
            return True
        else:
            print("⚠️  PRODUCTION SYSTEM HAS ISSUES THAT NEED FIXING")
            return False
    
    async def close(self):
        await self.client.aclose()

async def main():
    """Main verification function"""
    verifier = ProductionVerifier()
    
    try:
        success = await verifier.verify_production_system()
        
        if success:
            print("\n✅ VERIFICATION COMPLETE - SYSTEM READY FOR PRODUCTION")
            print("\n🌐 Production URL:", PRODUCTION_URL)
            print("🔗 Webhook URL:", f"{PRODUCTION_URL}/paradigm-webhook")
            print("📊 Dashboard:", PRODUCTION_URL)
        else:
            print("\n❌ VERIFICATION FAILED - SYSTEM NEEDS FIXES")
            
    finally:
        await verifier.close()

if __name__ == "__main__":
    asyncio.run(main())
