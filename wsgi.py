#!/usr/bin/env python3
import os
import sys
from waitress import serve

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask application
from inventory_system_24_7 import app

# Configure for production
app.config['DEBUG'] = False
app.config['ENV'] = 'production'

def create_app():
    '''Application factory for Render'''
    return app

if __name__ == '__main__':
    # Get port from environment (Render sets this automatically)
    port = int(os.environ.get('PORT', 8000))
    
    print(f"🚀 Greenfield Inventory System starting on port {port}")
    print("🌐 Professional AI-Powered Inventory Management")
    print("✅ Real-time Paradigm ERP Integration")
    print("🧠 Advanced Natural Language Processing")
    
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
