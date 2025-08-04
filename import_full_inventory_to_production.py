#!/usr/bin/env python3
"""
Import full inventory to production Render system
"""
import requests
import csv
import json
import time

# Production URL
PRODUCTION_URL = "https://greenfield-inventory-system.onrender.com"

def import_inventory_to_production():
    """Import all products from CSV to production system"""
    
    print("🚀 Starting import to production system...")
    print(f"📊 Target: {PRODUCTION_URL}")
    
    # Read the full inventory CSV
    try:
        with open('full_inventory_import.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            products = list(reader)
            
        print(f"📋 Found {len(products)} products to import")
        
    except FileNotFoundError:
        print("❌ full_inventory_import.csv not found!")
        return False
    
    # Import products in batches
    batch_size = 100
    imported = 0
    failed = 0
    
    for i in range(0, len(products), batch_size):
        batch = products[i:i + batch_size]
        
        print(f"📦 Importing batch {i//batch_size + 1} ({len(batch)} products)...")
        
        # Prepare batch data
        batch_data = []
        for product in batch:
            batch_data.append({
                'product_id': product.get('ProductID', '').strip(),
                'description': product.get('Description', '').strip(),
                'quantity': int(float(product.get('Quantity', 0) or 0))
            })
        
        # Send batch to production
        try:
            response = requests.post(
                f"{PRODUCTION_URL}/api/bulk-import",
                json={'products': batch_data},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    imported += len(batch)
                    print(f"✅ Batch imported successfully ({imported} total)")
                else:
                    failed += len(batch)
                    print(f"❌ Batch failed: {result.get('error')}")
            else:
                failed += len(batch)
                print(f"❌ HTTP {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            failed += len(batch)
            print(f"❌ Request failed: {e}")
        
        # Small delay between batches
        time.sleep(1)
    
    print(f"\n🎉 Import complete!")
    print(f"✅ Successfully imported: {imported} products")
    print(f"❌ Failed: {failed} products")
    print(f"📊 Total processed: {imported + failed} products")
    
    return imported > 0

if __name__ == "__main__":
    import_inventory_to_production()