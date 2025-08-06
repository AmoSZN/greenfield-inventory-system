#!/usr/bin/env python3
"""
Monitor production deployment status
"""

import asyncio
import httpx
import time
from datetime import datetime

PRODUCTION_URL = "https://greenfield-inventory-system.onrender.com"

async def check_deployment():
    """Check if new version is deployed"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Check for v2.1 in health endpoint
            response = await client.get(f"{PRODUCTION_URL}/health")
            if response.status_code == 200:
                data = response.json()
                version = data.get("version", "unknown")
                if version == "2.1":
                    return True, "v2.1 DEPLOYED"
                else:
                    return False, f"Old version still running"
            else:
                return False, f"Health check failed: {response.status_code}"
        except Exception as e:
            return False, f"Error: {e}"

async def monitor():
    """Monitor deployment progress"""
    print("🔍 MONITORING PRODUCTION DEPLOYMENT")
    print("=" * 50)
    print(f"URL: {PRODUCTION_URL}")
    print("Waiting for v2.1 deployment...\n")
    
    start_time = time.time()
    check_count = 0
    max_checks = 60  # Check for up to 10 minutes
    
    while check_count < max_checks:
        check_count += 1
        elapsed = int(time.time() - start_time)
        
        deployed, status = await check_deployment()
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] Check #{check_count} ({elapsed}s): {status}")
        
        if deployed:
            print("\n" + "=" * 50)
            print("🎉 DEPLOYMENT SUCCESSFUL!")
            print(f"✅ Version 2.1 is now live at {PRODUCTION_URL}")
            
            # Run full verification
            print("\nRunning full system verification...")
            await verify_system()
            return True
        
        # Wait 10 seconds before next check
        await asyncio.sleep(10)
    
    print("\n" + "=" * 50)
    print("❌ DEPLOYMENT TIMEOUT - Manual intervention required")
    return False

async def verify_system():
    """Verify all endpoints are working"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        endpoints = [
            ("/health", "Health Check"),
            ("/api/stats", "API Stats"),
            ("/test-webhook", "Webhook Test"),
        ]
        
        print("\n📊 SYSTEM VERIFICATION:")
        for endpoint, description in endpoints:
            try:
                response = await client.get(f"{PRODUCTION_URL}{endpoint}")
                if response.status_code == 200:
                    print(f"✅ {description}: WORKING")
                else:
                    print(f"❌ {description}: Status {response.status_code}")
            except Exception as e:
                print(f"❌ {description}: ERROR")

if __name__ == "__main__":
    asyncio.run(monitor())
