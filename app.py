#!/usr/bin/env python3
"""
Greenfield Metal Sales - Production Inventory System v2.3
Main entry point for Render.com deployment
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import the production app
from production_app_fixed import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)