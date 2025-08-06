#!/usr/bin/env python3
"""
Start System Fixed - Run on different port to avoid conflicts
"""

import uvicorn
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Starting Greenfield Inventory System on port 8001...")
    print("📊 Database should be fixed and ready")
    print("🌐 Access at: http://localhost:8001")
    print("Press Ctrl+C to stop")
    
    uvicorn.run(
        "hybrid_smart_inventory:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )
