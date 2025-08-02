#!/usr/bin/env python3
"""
Direct Bulk Import for Greenfield Inventory System
Import products directly into the database from CSV
"""

import sqlite3
import csv
import os
from datetime import datetime
import sys

def import_csv_to_db(csv_file):
    """Import CSV directly to inventory database"""
    print(f"📤 Direct Bulk Import Tool")
    print("=" * 50)
    
    # Check if CSV exists
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        print("\nUsage: python direct_bulk_import.py <your_csv_file.csv>")
        return
    
    # Connect to database
    db_path = 'Data/inventory.db'
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        print("Make sure the inventory system has run at least once.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    imported = 0
    updated = 0
    errors = 0
    
    print(f"\n📂 Reading: {csv_file}")
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row_num, row in enumerate(reader, 1):
            try:
                # Get values from CSV
                product_id = row.get('ProductID', '').strip()
                if not product_id:
                    print(f"⚠️  Row {row_num}: Missing ProductID, skipping")
                    errors += 1
                    continue
                
                description = row.get('Description', '')
                quantity = float(row.get('Quantity', 0))
                notes = row.get('Notes', '')
                
                # Try to insert
                try:
                    cursor.execute('''
                        INSERT INTO items 
                        (product_id, description, quantity, last_updated, times_accessed, verified)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (product_id, description, quantity, datetime.now(), 0, 1))
                    imported += 1
                    if imported % 100 == 0:
                        print(f"   Imported {imported} products...")
                except sqlite3.IntegrityError:
                    # Update existing
                    cursor.execute('''
                        UPDATE items 
                        SET description = ?, quantity = ?, last_updated = ?, verified = 1
                        WHERE product_id = ?
                    ''', (description, quantity, datetime.now(), product_id))
                    updated += 1
                    
            except Exception as e:
                print(f"❌ Row {row_num} error: {str(e)}")
                errors += 1
    
    # Commit changes
    conn.commit()
    
    # Get total count
    cursor.execute("SELECT COUNT(*) FROM items")
    total_count = cursor.fetchone()[0]
    
    conn.close()
    
    print("\n" + "=" * 50)
    print(f"📊 Import Summary:")
    print(f"   File: {csv_file}")
    print(f"   New Products: {imported}")
    print(f"   Updated: {updated}")
    print(f"   Errors: {errors}")
    print(f"   Total in Database: {total_count}")
    print("\n✅ Import complete!")
    print("🌐 View at: http://localhost:8000")

def create_sample_csv():
    """Create a sample CSV template"""
    sample_file = 'sample_inventory_import.csv'
    with open(sample_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ProductID', 'Quantity', 'Description', 'Notes'])
        writer.writerow(['2001AL', '100', 'Aluminum Sheet 2001', 'Sample product'])
        writer.writerow(['2002BR', '200', 'Brass Rod 2002', 'Sample product'])
        writer.writerow(['2003CU', '150', 'Copper Wire 2003', 'Sample product'])
    
    print(f"📄 Created sample template: {sample_file}")
    print("Edit this file and run: python direct_bulk_import.py sample_inventory_import.csv")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        import_csv_to_db(csv_file)
    else:
        print("📤 Direct Bulk Import Tool")
        print("=" * 50)
        print("\nUsage: python direct_bulk_import.py <your_csv_file.csv>")
        print("\nCreating sample template...")
        create_sample_csv()