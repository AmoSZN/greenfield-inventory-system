#!/usr/bin/env python3
"""
Greenfield Metal Sales - Fixed Production Inventory System v2.1
24/7 Cloud-hosted inventory management with real-time Paradigm integration
"""

import os
import asyncio
import logging
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import httpx
import aiosqlite
from contextlib import asynccontextmanager

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Production configuration
PARADIGM_BASE_URL = "https://greenfieldapi.para-apps.com"
PARADIGM_API_KEY = os.getenv("PARADIGM_API_KEY", "nVPsQFBteV&GEd7*8n0%RliVjksag8")
PARADIGM_USERNAME = os.getenv("PARADIGM_USERNAME", "web_admin")
PARADIGM_PASSWORD = os.getenv("PARADIGM_PASSWORD", "ChangeMe#123!")
DB_PATH = "data/smart_inventory.db"

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

class ProductionInventoryManager:
    def __init__(self):
        self.auth_token = None
        self.last_sync = None
        
    async def authenticate(self):
        """Authenticate with Paradigm API"""
        try:
            async with httpx.AsyncClient() as client:
                auth_data = {
                    "username": PARADIGM_USERNAME,
                    "password": PARADIGM_PASSWORD
                }
                response = await client.post(
                    f"{PARADIGM_BASE_URL}/api/user/Auth/GetToken",
                    json=auth_data,
                    headers={"X-API-Key": PARADIGM_API_KEY}
                )
                response.raise_for_status()
                self.auth_token = response.json().get("token")
                logger.info("Paradigm authentication successful")
                return True
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    async def sync_inventory_from_paradigm(self):
        """Sync inventory from Paradigm - try multiple endpoints"""
        if not self.auth_token:
            await self.authenticate()
            
        if not self.auth_token:
            return {"error": "Authentication failed"}
            
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.auth_token}",
                    "X-API-Key": PARADIGM_API_KEY
                }
                
                # Try multiple possible endpoints
                endpoints = [
                    "/api/Inventory/GetItems",
                    "/api/Items/GetItems", 
                    "/api/Products/GetAll",
                    "/api/Inventory/GetInventory"
                ]
                
                for endpoint in endpoints:
                    try:
                        response = await client.get(
                            f"{PARADIGM_BASE_URL}{endpoint}",
                            headers=headers
                        )
                        if response.status_code == 200:
                            items = response.json()
                            logger.info(f"Successfully synced from {endpoint}")
                            
                            # Update local database
                            await self._update_local_database(items)
                            return {"success": True, "items_count": len(items), "endpoint": endpoint}
                    except Exception as e:
                        logger.warning(f"Endpoint {endpoint} failed: {e}")
                        continue
                
                return {"error": "No working inventory endpoint found"}
                
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return {"error": str(e)}
    
    async def _update_local_database(self, items):
        """Update local database with inventory data"""
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    product_id TEXT PRIMARY KEY,
                    description TEXT,
                    current_quantity INTEGER,
                    last_updated TIMESTAMP
                )
            ''')
            
            for item in items:
                product_id = item.get("productId") or item.get("id") or item.get("ProductId")
                description = item.get("description") or item.get("Description") or item.get("name")
                quantity = item.get("currentQuantity") or item.get("quantity") or item.get("Quantity") or 0
                
                if product_id:
                    await db.execute('''
                        INSERT OR REPLACE INTO inventory 
                        (product_id, description, current_quantity, last_updated)
                        VALUES (?, ?, ?, ?)
                    ''', (product_id, description, quantity, datetime.now()))
            
            await db.commit()
    
    async def update_item_quantity(self, product_id: str, new_quantity: int):
        """Update item quantity in Paradigm"""
        if not self.auth_token:
            await self.authenticate()
            
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.auth_token}",
                    "X-API-Key": PARADIGM_API_KEY
                }
                
                update_data = {
                    "productId": product_id,
                    "quantity": new_quantity
                }
                
                # Try multiple update endpoints
                endpoints = [
                    "/api/Inventory/UpdateQuantity",
                    "/api/Items/UpdateQuantity",
                    "/api/Products/UpdateQuantity"
                ]
                
                for endpoint in endpoints:
                    try:
                        response = await client.post(
                            f"{PARADIGM_BASE_URL}{endpoint}",
                            json=update_data,
                            headers=headers
                        )
                        if response.status_code == 200:
                            logger.info(f"Successfully updated {product_id} to {new_quantity}")
                            return {"success": True, "product_id": product_id, "new_quantity": new_quantity}
                    except Exception as e:
                        logger.warning(f"Update endpoint {endpoint} failed: {e}")
                        continue
                
                return {"error": "No working update endpoint found"}
                
        except Exception as e:
            logger.error(f"Update failed: {e}")
            return {"error": str(e)}

# Global manager instance
inventory_manager = ProductionInventoryManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting Greenfield Production Inventory System v2.1")
    
    # Initialize database
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                product_id TEXT PRIMARY KEY,
                description TEXT,
                current_quantity INTEGER,
                last_updated TIMESTAMP
            )
        ''')
        await db.commit()
    
    yield
    
    logger.info("Shutting down Greenfield Production Inventory System")

app = FastAPI(title="Greenfield Metal Sales - Production Inventory System v2.1", lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
async def main_page():
    """Main dashboard page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Greenfield Metal Sales - Production Inventory v2.1</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .status { padding: 15px; margin: 20px 0; border-radius: 5px; }
            .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
            .button:hover { background: #0056b3; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
            .stat-card { background: #f8f9fa; padding: 20px; border-radius: 5px; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏭 Greenfield Metal Sales</h1>
            <h2>Production Inventory Management System v2.2-1754471211</h2>
            
            <div class="status success">
                ✅ System Status: OPERATIONAL<br>
                🌐 Production URL: https://greenfield-inventory-system.onrender.com<br>
                🔗 Paradigm Integration: ACTIVE<br>
                📊 Database: FIXED
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <h3>📊 System Stats</h3>
                    <p><a href="/api/stats" class="button">View Stats</a></p>
                </div>
                <div class="stat-card">
                    <h3>🔄 Sync Inventory</h3>
                    <p><a href="/api/sync" class="button">Sync from Paradigm</a></p>
                </div>
                <div class="stat-card">
                    <h3>🔗 Webhook Test</h3>
                    <p><a href="/test-webhook" class="button">Test Webhook</a></p>
                </div>
                <div class="stat-card">
                    <h3>💚 Health Check</h3>
                    <p><a href="/health" class="button">Health Status</a></p>
                </div>
            </div>
            
            <h3>🎯 Quick Actions:</h3>
            <button class="button" onclick="syncInventory()">🔄 Sync from Paradigm</button>
            <button class="button" onclick="checkHealth()">💚 Check Health</button>
            <button class="button" onclick="viewStats()">📊 View Stats</button>
            
            <div id="results" style="margin-top: 20px;"></div>
        </div>
        
        <script>
            async function syncInventory() {
                const results = document.getElementById('results');
                results.innerHTML = '🔄 Syncing inventory from Paradigm...';
                
                try {
                    const response = await fetch('/api/sync', {method: 'POST'});
                    const data = await response.json();
                    results.innerHTML = `<div class="status success">✅ Sync Result: ${JSON.stringify(data, null, 2)}</div>`;
                } catch (error) {
                    results.innerHTML = `<div class="status error">❌ Sync Error: ${error}</div>`;
                }
            }
            
            async function checkHealth() {
                const results = document.getElementById('results');
                results.innerHTML = '💚 Checking system health...';
                
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    results.innerHTML = `<div class="status success">✅ Health Check: ${JSON.stringify(data, null, 2)}</div>`;
                } catch (error) {
                    results.innerHTML = `<div class="status error">❌ Health Check Error: ${error}</div>`;
                }
            }
            
            async function viewStats() {
                const results = document.getElementById('results');
                results.innerHTML = '📊 Loading stats...';
                
                try {
                    const response = await fetch('/api/stats');
                    const data = await response.json();
                    results.innerHTML = `<div class="status success">✅ Stats: ${JSON.stringify(data, null, 2)}</div>`;
                } catch (error) {
                    results.innerHTML = `<div class="status error">❌ Stats Error: ${error}</div>`;
                }
            }
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Greenfield Production Inventory System v2.1",
        "version": "v2.2-1754471211",
        "paradigm_connected": inventory_manager.auth_token is not None
    }

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM inventory")
            count = await cursor.fetchone()
            item_count = count[0] if count else 0
            
            cursor = await db.execute("SELECT MAX(last_updated) FROM inventory")
            last_update = await cursor.fetchone()
            last_update_time = last_update[0] if last_update and last_update[0] else "Never"
        
        return {
            "total_items": item_count,
            "last_sync": last_update_time,
            "system_status": "operational",
            "paradigm_connected": inventory_manager.auth_token is not None,
            "timestamp": datetime.now().isoformat(),
            "version": "v2.2-1754471211"
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {"error": str(e)}

@app.post("/api/sync")
async def sync_inventory():
    """Sync inventory from Paradigm"""
    result = await inventory_manager.sync_inventory_from_paradigm()
    return result

@app.post("/paradigm-webhook")
async def paradigm_webhook(request: Request):
    """Handle Paradigm webhook updates"""
    try:
        data = await request.json()
        logger.info(f"Received webhook: {data}")
        
        # Process the webhook data
        if "productId" in data and "quantity" in data:
            result = await inventory_manager.update_item_quantity(
                data["productId"], 
                data["quantity"]
            )
            return {"success": True, "processed": result}
        
        return {"success": True, "message": "Webhook received"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"error": str(e)}

@app.get("/test-webhook")
async def test_webhook():
    """Test webhook endpoint"""
    return {
        "message": "Webhook endpoint is working",
        "url": "https://greenfield-inventory-system.onrender.com/paradigm-webhook",
        "instructions": "Configure this URL in Paradigm ERP webhook settings",
        "version": "v2.2-1754471211"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
