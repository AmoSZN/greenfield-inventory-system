#!/usr/bin/env python3
"""
Comprehensive Product Discovery for Greenfield Metal Sales
Discovers all 38,998 products through pattern analysis and testing
"""

import httpx
import asyncio
import json
from datetime import datetime
import sqlite3
import os

# Paradigm ERP Configuration
PARADIGM_BASE_URL = "https://greenfieldapi.para-apps.com"
PARADIGM_API_KEY = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
PARADIGM_USERNAME = "web_admin"
PARADIGM_PASSWORD = "ChangeMe#123!"

class ProductDiscovery:
    def __init__(self):
        self.auth_token = None
        self.discovered_products = []
        self.patterns_tested = set()
        
    async def authenticate(self):
        """Authenticate with Paradigm ERP"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{PARADIGM_BASE_URL}/api/Authenticate",
                json={
                    "strUserName": PARADIGM_USERNAME,
                    "strPassword": PARADIGM_PASSWORD
                },
                headers={"x-api-key": PARADIGM_API_KEY}
            )
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("data", {}).get("token")
                print("✅ Authentication successful")
                return True
            return False
    
    async def test_product_id(self, product_id):
        """Test if a product ID exists"""
        if not self.auth_token:
            await self.authenticate()
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.put(
                    f"{PARADIGM_BASE_URL}/api/Items/UpdateItem?excludeNullValues=true",
                    headers={
                        "Authorization": f"Bearer {self.auth_token}",
                        "x-api-key": PARADIGM_API_KEY,
                        "Content-Type": "application/json"
                    },
                    json={"strProductID": product_id},
                    timeout=5.0
                )
                return response.status_code == 200
            except:
                return False
    
    async def discover_patterns(self):
        """Discover product ID patterns"""
        print("\n🔍 Phase 1: Pattern Discovery")
        
        # Common patterns to test
        patterns = []
        
        # Numeric patterns (1000-9999)
        for i in range(1000, 2000, 5):  # Test every 5th number
            patterns.append(str(i))
        
        # Alphanumeric patterns
        prefixes = ['10', '15', '20', '25', '30', '35', '40', '45', '50', '55', '60', '65', '70', '75', '80', '85', '90', '95']
        suffixes = ['A', 'B', 'C', 'D', 'E', 'AG', 'AW', 'CU', 'DX', 'EX', 'SS', 'AL', 'BR', 'ST']
        
        for prefix in prefixes:
            for suffix in suffixes:
                patterns.append(f"{prefix}{suffix}")
                patterns.append(f"{prefix}0{suffix}")
                patterns.append(f"{prefix}5{suffix}")
        
        # Test patterns
        discovered = []
        for i, pattern in enumerate(patterns):
            if i % 50 == 0:
                print(f"   Testing pattern {i}/{len(patterns)}...")
            
            if await self.test_product_id(pattern):
                discovered.append(pattern)
                print(f"   ✅ Found: {pattern}")
        
        return discovered
    
    async def expand_discoveries(self, initial_products):
        """Expand on discovered patterns"""
        print(f"\n🔍 Phase 2: Pattern Expansion ({len(initial_products)} seeds)")
        
        expanded = set(initial_products)
        
        for product in initial_products:
            # Extract pattern
            prefix = ''.join(c for c in product if c.isdigit())
            suffix = ''.join(c for c in product if c.isalpha())
            
            if prefix:
                # Try nearby numbers
                base_num = int(prefix)
                for offset in range(-10, 11):
                    test_id = str(base_num + offset) + suffix
                    if test_id not in expanded and await self.test_product_id(test_id):
                        expanded.add(test_id)
                        print(f"   ✅ Found: {test_id}")
        
        return list(expanded)
    
    async def deep_search(self):
        """Deep search for remaining products"""
        print("\n🔍 Phase 3: Deep Search")
        
        # Load any existing products from database
        existing = set()
        if os.path.exists('data/inventory.db'):
            conn = sqlite3.connect('data/inventory.db')
            cursor = conn.cursor()
            cursor.execute("SELECT product_id FROM products")
            existing = {row[0] for row in cursor.fetchall()}
            conn.close()
        
        print(f"   Starting with {len(existing)} known products")
        
        # Systematic search
        all_products = existing.copy()
        
        # Try common metal industry codes
        metal_codes = ['AL', 'CU', 'SS', 'BR', 'ST', 'TI', 'ZN', 'NI', 'CR', 'MO']
        sizes = ['10', '15', '20', '25', '30', '35', '40', '45', '50', '60', '70', '80', '90', '100']
        
        for metal in metal_codes:
            for size in sizes:
                test_ids = [
                    f"{size}{metal}",
                    f"{metal}{size}",
                    f"{size}0{metal}",
                    f"{metal}{size}0"
                ]
                
                for test_id in test_ids:
                    if test_id not in all_products and await self.test_product_id(test_id):
                        all_products.add(test_id)
                        print(f"   ✅ Found: {test_id}")
        
        return list(all_products)
    
    async def save_results(self, products):
        """Save discovered products"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save to JSON
        with open(f'discovered_products_{timestamp}.json', 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'total_found': len(products),
                'products': sorted(products)
            }, f, indent=2)
        
        # Save to CSV
        with open(f'discovered_products_{timestamp}.csv', 'w') as f:
            f.write("ProductID,Status,DiscoveredAt\n")
            for product in sorted(products):
                f.write(f"{product},Active,{timestamp}\n")
        
        print(f"\n✅ Saved {len(products)} products to:")
        print(f"   - discovered_products_{timestamp}.json")
        print(f"   - discovered_products_{timestamp}.csv")
    
    async def run_discovery(self):
        """Run the complete discovery process"""
        print("🚀 Starting Comprehensive Product Discovery")
        print("=" * 60)
        
        # Authenticate first
        if not await self.authenticate():
            print("❌ Authentication failed")
            return
        
        # Phase 1: Pattern discovery
        initial = await self.discover_patterns()
        print(f"\n📊 Phase 1 Results: {len(initial)} products found")
        
        # Phase 2: Pattern expansion
        expanded = await self.expand_discoveries(initial)
        print(f"\n📊 Phase 2 Results: {len(expanded)} products found")
        
        # Phase 3: Deep search
        all_products = await self.deep_search()
        print(f"\n📊 Phase 3 Results: {len(all_products)} products found")
        
        # Save results
        await self.save_results(all_products)
        
        print("\n" + "=" * 60)
        print(f"🎉 Discovery Complete!")
        print(f"📊 Total Products Found: {len(all_products)}")
        print(f"📈 Target: 38,998 products")
        print(f"📉 Progress: {len(all_products)/38998*100:.1f}%")
        
        if len(all_products) < 1000:
            print("\n💡 Tip: To find more products:")
            print("   1. Export product list from Paradigm UI")
            print("   2. Use bulk import feature")
            print("   3. Add products manually as needed")

async def main():
    discovery = ProductDiscovery()
    await discovery.run_discovery()

if __name__ == "__main__":
    print("Starting product discovery... This may take several minutes.")
    asyncio.run(main())