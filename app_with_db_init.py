#!/usr/bin/env python3
"""
Greenfield Inventory System - Production Entry Point with Database Initialization
This is the main entry point for Render.com deployment with database setup
"""
import os
import sys
import sqlite3
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
        
        logger.info(f"🔧 Initializing database at: {db_path}")
        
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
            logger.info("📊 Adding sample inventory data...")
            sample_items = [
                ('1015B', 'Steel Bar 15mm x 3m', 100),
                ('1020B', 'Steel Bar 20mm x 3m', 75),
                ('1025AW', 'Aluminum Wire 25mm', 50),
                ('STEEL-001', 'Premium Steel Sheet', 200),
                ('ALUM-002', 'Aluminum Plate', 150),
                ('COPPER-003', 'Copper Wire 12AWG', 300),
                ('IRON-004', 'Iron Rod 10mm', 125),
                ('BRASS-005', 'Brass Fitting 1/2"', 80),
            ]
            
            for product_id, desc, qty in sample_items:
                c.execute('''INSERT OR IGNORE INTO items 
                           (product_id, description, quantity) 
                           VALUES (?, ?, ?)''', (product_id, desc, qty))
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Database initialized successfully!")
        logger.info(f"📊 Database ready at: {os.path.abspath(db_path)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Initialize database first
logger.info("🚀 Starting Greenfield Inventory System")
logger.info("🔧 Initializing database...")

if not init_database():
    logger.error("❌ Failed to initialize database - exiting")
    sys.exit(1)

try:
    # Import the Flask application
    from inventory_system_24_7 import app
    
    # Configure for production
    app.config['DEBUG'] = False
    app.config['ENV'] = 'production'
    
    logger.info("✅ Flask app imported successfully")
    logger.info("✅ Database initialization complete")
    
except Exception as e:
    logger.error(f"❌ Error importing Flask app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# WSGI application for Render
application = app

if __name__ == '__main__':
    # Get port from environment (Render sets this automatically)
    port = int(os.environ.get('PORT', 10000))
    
    logger.info(f"🚀 Greenfield Inventory System starting on port {port}")
    logger.info("🌐 Professional AI-Powered Inventory Management")
    logger.info("✅ Real-time Paradigm ERP Integration")
    logger.info("🧠 Advanced Natural Language Processing")
    logger.info("📊 Database ready with sample data")
    
    try:
        from waitress import serve
        # Use Waitress WSGI server (production-ready)
        serve(
            app,
            host='0.0.0.0',
            port=port,
            threads=6,
            connection_limit=1000,
            cleanup_interval=30,
            channel_timeout=120
        )
    except ImportError:
        logger.warning("⚠️ Waitress not available, using Flask dev server")
        app.run(host='0.0.0.0', port=port, debug=False)