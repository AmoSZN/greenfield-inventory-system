#!/usr/bin/env python3
"""
Main entry point for production deployment
This file ensures the correct application is loaded
"""

# Import the fixed production app
from production_app_fixed import app

# This is what Render.com will run
if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
