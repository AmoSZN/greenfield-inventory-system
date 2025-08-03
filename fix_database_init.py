#!/usr/bin/env python3
"""
Quick fix for Render deployment - Initialize database on startup
"""
import sqlite3
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database with all required tables"""
    try:
        # Ensure the Data directory exists
        os.makedirs('Data', exist_ok=True)
        
        # Database path
        db_path = 'Data/inventory.db'
        
        logger.info(f"Initializing database at: {db_path}")
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Create items table
        c.execute('''CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT UNIQUE NOT NULL,
            description TEXT,
            quantity INTEGER DEFAULT 0,
            notes TEXT,
            times_accessed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Create update_history table
        c.execute('''CREATE TABLE IF NOT EXISTS update_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT NOT NULL,
            field_updated TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_by TEXT DEFAULT 'system'
        )''')
        
        # Create search_history table
        c.execute('''CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_term TEXT NOT NULL,
            results_count INTEGER DEFAULT 0,
            searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Add some sample data if tables are empty
        c.execute('SELECT COUNT(*) FROM items')
        item_count = c.fetchone()[0]
        
        if item_count == 0:
            logger.info("Adding sample inventory data...")
            sample_items = [
                ('1015B', 'Steel Bar 15mm x 3m', 100),
                ('1020B', 'Steel Bar 20mm x 3m', 75),
                ('1025AW', 'Aluminum Wire 25mm', 50),
                ('STEEL-001', 'Premium Steel Sheet', 200),
                ('ALUM-002', 'Aluminum Plate', 150),
            ]
            
            for product_id, desc, qty in sample_items:
                c.execute('''INSERT OR IGNORE INTO items 
                           (product_id, description, quantity) 
                           VALUES (?, ?, ?)''', (product_id, desc, qty))
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Database initialized successfully!")
        logger.info(f"✅ Database file created at: {os.path.abspath(db_path)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    init_database()