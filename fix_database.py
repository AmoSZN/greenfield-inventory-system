#!/usr/bin/env python3
"""
Fix Database - Initialize missing tables
"""

import sqlite3
import os
from pathlib import Path

def fix_database():
    """Initialize the database with missing tables"""
    
    # Ensure data directory exists
    Path("data").mkdir(exist_ok=True)
    
    db_path = "data/smart_inventory.db"
    
    print(f"Connecting to database: {db_path}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create items table
        print("Creating items table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                product_id TEXT PRIMARY KEY,
                description TEXT,
                category TEXT,
                subcategory TEXT,
                current_quantity INTEGER,
                last_updated TIMESTAMP,
                times_accessed INTEGER DEFAULT 0,
                last_accessed TIMESTAMP,
                is_verified BOOLEAN DEFAULT 0,
                custom_fields TEXT
            )
        ''')
        
        # Create search_patterns table
        print("Creating search_patterns table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_patterns (
                pattern TEXT PRIMARY KEY,
                frequency INTEGER DEFAULT 1,
                last_used TIMESTAMP
            )
        ''')
        
        # Create update_history table
        print("Creating update_history table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS update_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT,
                old_quantity INTEGER,
                new_quantity INTEGER,
                update_time TIMESTAMP,
                user_id TEXT,
                notes TEXT
            )
        ''')
        
        # Commit changes
        conn.commit()
        
        # Verify tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"Database tables created: {[table[0] for table in tables]}")
        
        # Check if items table has any data
        cursor.execute("SELECT COUNT(*) FROM items")
        count = cursor.fetchone()[0]
        print(f"Items in database: {count}")
        
        print("✅ Database fixed successfully!")
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database()
