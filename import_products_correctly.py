#!/usr/bin/env python3
"""
Import Products Correctly into Inventory System Database
"""

import sqlite3
import os
from datetime import datetime

# Known Product IDs from previous discovery
KNOWN_PRODUCTS = {
    "1010AG": "Aluminum Grade A - 10mm",
    "1015AW": "Aluminum Wire - 15mm",
    "1020B": "Bronze Sheet Type B",
    "1025AW": "Aluminum Wire - 25mm",
    "1030C": "Copper Plate Type C",
    "1035CU": "Copper Unit - 35mm",
    "1040D": "Steel Grade D",
    "1045DX": "Steel Deluxe - 45mm",
    "1050E": "Electrode Type E",
    "1055EX": "Electrode Extra",
    # Add more as discovered
}

def import_to_inventory_db():
    """Import products into the inventory system database"""
    print("🚀 Importing Products to Inventory System")
    print("=" * 50)
    
    # Connect to the inventory database
    db_path = 'Data/inventory.db'  # Note: Capital 'D' in Data
    
    if not os.path.exists(db_path):
        print("❌ Database not found. Make sure inventory system has run at least once.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    imported = 0
    updated = 0
    
    for product_id, description in KNOWN_PRODUCTS.items():
        try:
            # Try to insert new product
            cursor.execute('''
                INSERT INTO items (product_id, description, quantity, last_updated, times_accessed, verified)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (product_id, description, 0, datetime.now(), 0, 1))
            imported += 1
            print(f"✅ Added: {product_id} - {description}")
        except sqlite3.IntegrityError:
            # Product exists, update it
            cursor.execute('''
                UPDATE items 
                SET description = ?, verified = 1, last_updated = ?
                WHERE product_id = ?
            ''', (description, datetime.now(), product_id))
            updated += 1
            print(f"📝 Updated: {product_id}")
    
    conn.commit()
    
    # Get total count
    cursor.execute("SELECT COUNT(*) FROM items")
    total_count = cursor.fetchone()[0]
    
    conn.close()
    
    print("\n" + "=" * 50)
    print(f"📊 Import Summary:")
    print(f"   New Products Added: {imported}")
    print(f"   Products Updated: {updated}")
    print(f"   Total in Database: {total_count}")
    
    # Restart the inventory system to see changes
    print("\n💡 Tip: Restart the inventory system to see the changes")
    print("   Or refresh the web page at http://localhost:8000")
    
    # Create a CSV for bulk import of remaining products
    print("\n📄 Creating template CSV for remaining products...")
    with open('remaining_products_template.csv', 'w') as f:
        f.write("ProductID,Quantity,Description,Notes\n")
        f.write("2000AL,0,Aluminum Sheet 2000 Series,Add your products here\n")
        f.write("3000BR,0,Brass Rod 3000 Series,Import via web interface\n")
    
    print("✅ Template saved as: remaining_products_template.csv")
    print("\n✅ Import complete!")

if __name__ == "__main__":
    import_to_inventory_db()