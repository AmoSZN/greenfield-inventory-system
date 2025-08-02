#!/usr/bin/env python3
"""
Import Paradigm Inventory Export
"""

import sqlite3
import pandas as pd
from datetime import datetime

print("🚀 Importing Paradigm Inventory")
print("=" * 60)

# Read the CSV with Paradigm column names
df = pd.read_csv('full_inventory_import.csv')
print(f"📊 Found {len(df)} products to import")

# Connect to database
conn = sqlite3.connect('Data/inventory.db')
cursor = conn.cursor()

# Prepare data for import
batch_size = 1000
total_imported = 0

for i in range(0, len(df), batch_size):
    batch = df.iloc[i:i+batch_size]
    
    # Prepare records
    records = []
    for _, row in batch.iterrows():
        product_id = str(row['StrProductID'])
        description = str(row['MemDescription']) if pd.notna(row['MemDescription']) else ''
        # No quantity in this export, so we'll set to 0
        quantity = 0
        
        records.append((
            product_id,
            description,
            quantity,
            datetime.now(),
            0,  # times_accessed
            1   # verified
        ))
    
    # Insert batch
    cursor.executemany('''
        INSERT OR REPLACE INTO items 
        (product_id, description, quantity, last_updated, times_accessed, verified)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', records)
    
    total_imported += len(records)
    print(f"   Imported {total_imported} / {len(df)} products...")

conn.commit()

# Get final count
cursor.execute("SELECT COUNT(*) FROM items")
total_in_db = cursor.fetchone()[0]

conn.close()

print(f"\n✅ Import Complete!")
print(f"   Products imported: {total_imported}")
print(f"   Total in database: {total_in_db}")
print(f"\n🎯 Ready for API Integration!")