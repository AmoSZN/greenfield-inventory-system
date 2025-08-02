#!/usr/bin/env python3
"""
Import Full Inventory from Paradigm Export
"""

import sqlite3
import csv
from datetime import datetime
import os

print("🚀 Importing Full Inventory (39,184 products)")
print("=" * 60)

# Read the CSV
with open('ready_to_import.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    
    # Connect to database
    conn = sqlite3.connect('Data/inventory.db')
    cursor = conn.cursor()
    
    imported = 0
    updated = 0
    batch = []
    
    for row in reader:
        product_id = row['ProductID']
        description = row['Description']
        quantity = float(row.get('Quantity', 0))
        
        batch.append((product_id, description, quantity, datetime.now(), 0, 1))
        
        # Process in batches of 1000
        if len(batch) >= 1000:
            cursor.executemany('''
                INSERT OR REPLACE INTO items 
                (product_id, description, quantity, last_updated, times_accessed, verified)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', batch)
            imported += len(batch)
            print(f"   Imported {imported} products...")
            batch = []
    
    # Process remaining
    if batch:
        cursor.executemany('''
            INSERT OR REPLACE INTO items 
            (product_id, description, quantity, last_updated, times_accessed, verified)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', batch)
        imported += len(batch)
    
    conn.commit()
    
    # Get final count
    cursor.execute("SELECT COUNT(*) FROM items")
    total = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n✅ Import Complete!")
    print(f"   Total in database: {total}")
    print(f"   Ready for API integration!")