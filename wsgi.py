#!/usr/bin/env python3
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Import the Flask application
    from inventory_system_24_7 import app
    
    # Configure for production
    app.config['DEBUG'] = False
    app.config['ENV'] = 'production'
    
    print("✅ Flask app imported successfully")
    
except Exception as e:
    print(f"❌ Error importing Flask app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# WSGI application for Render
application = app

if __name__ == '__main__':
    # Get port from environment (Render sets this automatically)
    port = int(os.environ.get('PORT', 8000))
    
    print(f"🚀 Greenfield Inventory System starting on port {port}")
    print("🌐 Professional AI-Powered Inventory Management")
    print("✅ Real-time Paradigm ERP Integration")
    print("🧠 Advanced Natural Language Processing")
    
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
        print("⚠️ Waitress not available, using Flask dev server")
        app.run(host='0.0.0.0', port=port, debug=False)
