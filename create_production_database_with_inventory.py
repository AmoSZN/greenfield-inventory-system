#!/usr/bin/env python3
"""
Create a complete database initialization script that includes all inventory
This will be added to the app.py startup to populate the database on deployment
"""
import csv

def generate_database_init_code():
    """Generate Python code to initialize database with all products"""
    
    print("📋 Reading full_inventory_import.csv...")
    
    # Read all products from CSV
    products = []
    try:
        with open('full_inventory_import.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                product_id = row.get('StrProductID', '').strip()
                if product_id:
                    products.append({
                        'product_id': product_id,
                        'description': row.get('MemDescription', '').strip()[:255]  # Limit length
                    })
        
        print(f"✅ Found {len(products)} products")
        
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False
    
    # Generate the initialization code
    print("🔧 Generating database initialization code...")
    
    init_code = '''
        # Add all inventory products
        logger.info("📦 Adding full inventory...")
        inventory_products = [
'''
    
    # Add products in chunks to avoid massive single list
    chunk_size = 100
    for i in range(0, len(products), chunk_size):
        chunk = products[i:i + chunk_size]
        for product in chunk:
            # Escape single quotes in descriptions
            description = product['description'].replace("'", "''")
            init_code += f"            ('{product['product_id']}', '{description}', 0),\n"
    
    init_code += '''        ]
        
        for product_id, desc, qty in inventory_products:
            c.execute(\'\'\'INSERT OR IGNORE INTO items 
                       (product_id, description, quantity) 
                       VALUES (?, ?, ?)\'\'\', (product_id, desc, qty))
        
        logger.info(f"✅ Added {len(inventory_products)} products to database")
'''
    
    # Write to file
    with open('database_init_with_inventory.py', 'w', encoding='utf-8') as f:
        f.write(init_code)
    
    print(f"✅ Generated database initialization code with {len(products)} products")
    print("📄 Saved to: database_init_with_inventory.py")
    
    return True

if __name__ == "__main__":
    print("🏭 GREENFIELD INVENTORY - DATABASE INITIALIZATION GENERATOR")
    print("=" * 60)
    
    success = generate_database_init_code()
    
    if success:
        print("\n🎉 SUCCESS! Database initialization code generated.")
        print("\n📋 Next steps:")
        print("1. Copy the generated code into app.py")
        print("2. Push to GitHub")
        print("3. Render will redeploy with full inventory")
    else:
        print("\n❌ Failed to generate initialization code.")