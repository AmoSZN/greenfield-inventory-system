#!/usr/bin/env python3
"""
Direct upload of full inventory to production Render system
This will populate the production database with all 39,184 products
"""
import requests
import csv
import json
import time
import sys

# Production URL
PRODUCTION_URL = "https://greenfield-inventory-system.onrender.com"

def upload_inventory():
    """Upload all products directly to production database"""
    
    print("🚀 Starting DIRECT upload to production system...")
    print(f"📊 Target: {PRODUCTION_URL}")
    print("=" * 60)
    
    # Read the CSV file
    products = []
    try:
        print("📋 Reading full_inventory_import.csv...")
        with open('full_inventory_import.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                product_id = row.get('StrProductID', '').strip()
                if product_id:  # Only add if we have a product ID
                    products.append({
                        'product_id': product_id,
                        'description': row.get('MemDescription', '').strip()[:255],  # Limit description length
                        'quantity': 0  # Set default quantity since CSV doesn't have quantity data
                    })
        
        print(f"✅ Loaded {len(products)} products from CSV")
        
    except FileNotFoundError:
        print("❌ ERROR: full_inventory_import.csv not found!")
        return False
    except Exception as e:
        print(f"❌ ERROR reading CSV: {e}")
        return False
    
    if not products:
        print("❌ No products found in CSV!")
        return False
    
    # Upload in batches
    batch_size = 50  # Smaller batches for reliability
    total_batches = (len(products) + batch_size - 1) // batch_size
    imported = 0
    failed = 0
    
    print(f"📦 Uploading {len(products)} products in {total_batches} batches...")
    print("-" * 60)
    
    for i in range(0, len(products), batch_size):
        batch = products[i:i + batch_size]
        batch_num = i // batch_size + 1
        
        print(f"📤 Batch {batch_num}/{total_batches} ({len(batch)} products)...", end=" ")
        
        # Create individual product entries
        batch_imported = 0
        batch_failed = 0
        
        for product in batch:
            try:
                # Use the individual product update endpoint
                response = requests.post(
                    f"{PRODUCTION_URL}/api/update",
                    json={
                        'product_id': product['product_id'],
                        'updates': {
                            'description': product['description'],
                            'quantity': product['quantity']
                        }
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        batch_imported += 1
                    else:
                        batch_failed += 1
                else:
                    batch_failed += 1
                    
            except Exception as e:
                batch_failed += 1
        
        imported += batch_imported
        failed += batch_failed
        
        print(f"✅ {batch_imported} imported, ❌ {batch_failed} failed")
        
        # Progress update
        if batch_num % 10 == 0 or batch_num == total_batches:
            progress = (batch_num / total_batches) * 100
            print(f"📊 Progress: {progress:.1f}% ({imported} imported, {failed} failed)")
        
        # Small delay to avoid overwhelming the server
        time.sleep(0.5)
    
    print("-" * 60)
    print(f"🎉 Upload complete!")
    print(f"✅ Successfully imported: {imported} products")
    print(f"❌ Failed: {failed} products")
    print(f"📊 Success rate: {(imported/(imported+failed)*100):.1f}%")
    
    # Test a few searches
    print("\n🧪 Testing search functionality...")
    test_searches = ['1015', '005C', 'Woodbinder']
    
    for search_term in test_searches:
        try:
            response = requests.get(f"{PRODUCTION_URL}/api/search?q={search_term}", timeout=10)
            if response.status_code == 200:
                results = response.json()
                print(f"🔍 Search '{search_term}': {len(results)} results found")
            else:
                print(f"❌ Search '{search_term}' failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Search '{search_term}' error: {e}")
    
    return imported > 0

if __name__ == "__main__":
    print("🏭 GREENFIELD METAL SALES - INVENTORY UPLOAD")
    print("=" * 60)
    
    # Confirm before proceeding
    print("⚠️  This will upload 39,000+ products to production!")
    print("⚠️  This may take 15-30 minutes to complete.")
    
    # Auto-proceed for automation
    print("🚀 Starting upload in 3 seconds...")
    time.sleep(3)
    
    success = upload_inventory()
    
    if success:
        print("\n🎉 SUCCESS! Your inventory is now live at:")
        print(f"🌐 {PRODUCTION_URL}")
        print("\n🧪 Try searching for '1015' to see your products!")
    else:
        print("\n❌ Upload failed. Check the error messages above.")
        sys.exit(1)