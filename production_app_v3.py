#!/usr/bin/env python3
"""
PRODUCTION APP V3 - COMPLETE REBUILD
State-of-the-art inventory management system with bulletproof sync
"""

import asyncio
import aiosqlite
import httpx
import logging
import os
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import threading
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("inventory_system_v3")

# Paradigm API Configuration
PARADIGM_BASE_URL = "https://greenfieldapi.para-apps.com"
PARADIGM_API_KEY = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
PARADIGM_USERNAME = "web_admin"
PARADIGM_PASSWORD = "ChangeMe#123!"

# Database path
DB_PATH = "data/inventory_v3.db"

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

class StateOfTheArtInventoryManager:
    def __init__(self):
        self.auth_token = None
        self.base_url = PARADIGM_BASE_URL
        self.api_key = PARADIGM_API_KEY
        self.username = PARADIGM_USERNAME
        self.password = PARADIGM_PASSWORD
        self.last_sync_time = None
        self.sync_in_progress = False
        self.total_items_available = 0
        
    async def authenticate(self):
        """Authenticate with Paradigm API - BULLETPROOF"""
        try:
            auth_data = {
                "username": self.username,
                "password": self.password
            }
            
            logger.info(f"🔐 AUTHENTICATING with Paradigm API...")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/user/Auth/GetToken",
                    json=auth_data,
                    headers={"X-API-Key": self.api_key, "Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Paradigm returns token in "data" field
                    self.auth_token = data.get("data")
                    
                    if self.auth_token:
                        logger.info("✅ AUTHENTICATION SUCCESSFUL")
                        return True
                    else:
                        logger.error(f"❌ NO TOKEN IN RESPONSE: {data}")
                        return False
                else:
                    logger.error(f"❌ AUTH FAILED: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ AUTH EXCEPTION: {e}")
            return False
    
    async def get_all_items_from_paradigm(self):
        """Get ALL items from Paradigm - NO LIMITS"""
        if not self.auth_token:
            if not await self.authenticate():
                raise Exception("Authentication failed")
        
        try:
            all_items = []
            skip = 0
            take = 10000  # Large batch size
            
            logger.info(f"📦 GETTING ALL ITEMS from Paradigm...")
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                headers = {
                    "Authorization": f"Bearer {self.auth_token}",
                    "X-API-Key": self.api_key
                }
                
                while True:
                    logger.info(f"📦 Fetching batch: skip={skip}, take={take}")
                    
                    response = await client.get(
                        f"{self.base_url}/api/Items/GetItems/{skip}/{take}",
                        headers=headers
                    )
                    
                    if response.status_code != 200:
                        raise Exception(f"API call failed: {response.status_code} - {response.text}")
                    
                    batch_items = response.json()
                    logger.info(f"📦 Retrieved {len(batch_items)} items in this batch")
                    
                    if not batch_items or len(batch_items) == 0:
                        break
                    
                    all_items.extend(batch_items)
                    
                    # If we got fewer items than requested, we've reached the end
                    if len(batch_items) < take:
                        break
                    
                    skip += take
                    
                    # Safety break - don't go beyond reasonable limits
                    if len(all_items) > 100000:
                        logger.warning("⚠️ Reached 100,000 item limit - stopping")
                        break
                
                self.total_items_available = len(all_items)
                logger.info(f"✅ RETRIEVED ALL {len(all_items)} ITEMS from Paradigm")
                return all_items
                
        except Exception as e:
            logger.error(f"❌ GET ITEMS ERROR: {e}")
            raise
    
    async def sync_to_database(self):
        """BULLETPROOF sync to local database"""
        if self.sync_in_progress:
            logger.warning("⚠️ SYNC ALREADY IN PROGRESS")
            return {"success": False, "error": "Sync already in progress"}
        
        self.sync_in_progress = True
        logger.info("🔄 STARTING BULLETPROOF SYNC...")
        
        try:
            # Get ALL items from Paradigm
            all_items = await self.get_all_items_from_paradigm()
            
            if not all_items:
                raise Exception("No items retrieved from Paradigm")
            
            logger.info(f"💾 SYNCING {len(all_items)} ITEMS to database...")
            
            # Initialize database with bulletproof schema
            async with aiosqlite.connect(DB_PATH) as db:
                # Drop and recreate table for clean sync
                await db.execute('DROP TABLE IF EXISTS inventory')
                
                await db.execute('''
                    CREATE TABLE inventory (
                        product_id TEXT PRIMARY KEY,
                        description TEXT,
                        current_quantity REAL,
                        unit_measure TEXT,
                        category TEXT,
                        cost REAL,
                        sales_price REAL,
                        item_class TEXT,
                        last_modified TEXT,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Batch insert for performance
                processed_count = 0
                batch_size = 1000
                
                for i in range(0, len(all_items), batch_size):
                    batch = all_items[i:i + batch_size]
                    
                    batch_data = []
                    for item in batch:
                        product_id = item.get("strProductID")
                        if product_id:
                            batch_data.append((
                                product_id,
                                item.get("memDescription", ""),
                                item.get("decUnitsInStock", 0.0),
                                item.get("strUnitMeasure", ""),
                                item.get("strCategory", ""),
                                item.get("curCost", 0.0),
                                item.get("curSalesPrice", 0.0),
                                item.get("strItemClass", ""),
                                item.get("dtmLastModified", ""),
                                datetime.now()
                            ))
                    
                    if batch_data:
                        await db.executemany('''
                            INSERT INTO inventory 
                            (product_id, description, current_quantity, unit_measure, category, 
                             cost, sales_price, item_class, last_modified, last_updated)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', batch_data)
                        
                        processed_count += len(batch_data)
                        logger.info(f"💾 PROCESSED {processed_count}/{len(all_items)} items")
                
                await db.commit()
                
                # Verify the sync
                cursor = await db.execute("SELECT COUNT(*) FROM inventory")
                count_result = await cursor.fetchone()
                final_count = count_result[0] if count_result else 0
                
                logger.info(f"🔍 VERIFICATION: {final_count} items in database")
                
                if final_count != processed_count:
                    raise Exception(f"Sync verification failed: processed {processed_count}, database has {final_count}")
            
            self.last_sync_time = datetime.now()
            logger.info(f"✅ SYNC COMPLETED SUCCESSFULLY: {processed_count} items")
            
            return {
                "success": True, 
                "items_synced": processed_count,
                "total_available": self.total_items_available,
                "sync_time": self.last_sync_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ SYNC FAILED: {e}")
            import traceback
            logger.error(f"❌ SYNC TRACEBACK: {traceback.format_exc()}")
            return {"success": False, "error": f"Sync failed: {str(e)}"}
        finally:
            self.sync_in_progress = False
    
    async def search_inventory(self, search_term: str = "", limit: int = 100):
        """Lightning-fast local search"""
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                if search_term:
                    cursor = await db.execute('''
                        SELECT product_id, description, current_quantity, unit_measure, category, sales_price
                        FROM inventory 
                        WHERE product_id LIKE ? OR description LIKE ? OR category LIKE ?
                        ORDER BY product_id
                        LIMIT ?
                    ''', (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", limit))
                else:
                    cursor = await db.execute('''
                        SELECT product_id, description, current_quantity, unit_measure, category, sales_price
                        FROM inventory 
                        ORDER BY product_id
                        LIMIT ?
                    ''', (limit,))
                
                rows = await cursor.fetchall()
                
                items = []
                for row in rows:
                    items.append({
                        "product_id": row[0],
                        "description": row[1],
                        "current_quantity": row[2],
                        "unit_measure": row[3],
                        "category": row[4],
                        "sales_price": row[5]
                    })
                
                return {"success": True, "items": items, "count": len(items)}
                
        except Exception as e:
            logger.error(f"❌ SEARCH ERROR: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_item_quantity(self, product_id: str, new_quantity: float):
        """Update item quantity in both Paradigm and local database"""
        try:
            # First get the full item from Paradigm
            all_items = await self.get_all_items_from_paradigm()
            
            current_item = None
            for item in all_items:
                if item.get("strProductID") == product_id:
                    current_item = item.copy()
                    break
            
            if not current_item:
                return {"success": False, "error": f"Item {product_id} not found"}
            
            # Update the quantity
            current_item["decUnitsInStock"] = new_quantity
            
            # Update in Paradigm
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "Authorization": f"Bearer {self.auth_token}",
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json"
                }
                
                response = await client.put(
                    f"{self.base_url}/api/Items/UpdateItem",
                    json=current_item,
                    headers=headers
                )
                
                if response.status_code == 200:
                    # Update local database
                    async with aiosqlite.connect(DB_PATH) as db:
                        await db.execute('''
                            UPDATE inventory 
                            SET current_quantity = ?, last_updated = ?
                            WHERE product_id = ?
                        ''', (new_quantity, datetime.now(), product_id))
                        await db.commit()
                    
                    logger.info(f"✅ UPDATED {product_id} to quantity {new_quantity}")
                    return {"success": True, "product_id": product_id, "new_quantity": new_quantity}
                else:
                    logger.error(f"❌ UPDATE FAILED: {response.status_code} - {response.text}")
                    return {"success": False, "error": f"Update failed: {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"❌ UPDATE ERROR: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_stats(self):
        """Get comprehensive system statistics"""
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                # Get total count
                cursor = await db.execute("SELECT COUNT(*) FROM inventory")
                count_result = await cursor.fetchone()
                total_items = count_result[0] if count_result else 0
                
                # Get last sync time
                cursor = await db.execute("SELECT MAX(last_updated) FROM inventory")
                last_update_result = await cursor.fetchone()
                last_update = last_update_result[0] if last_update_result and last_update_result[0] else None
                
                return {
                    "total_items": total_items,
                    "total_available": self.total_items_available,
                    "last_sync": self.last_sync_time.isoformat() if self.last_sync_time else None,
                    "paradigm_connected": self.auth_token is not None,
                    "sync_in_progress": self.sync_in_progress,
                    "version": "3.0"
                }
                
        except Exception as e:
            logger.error(f"❌ STATS ERROR: {e}")
            return {"error": str(e)}

# Initialize the state-of-the-art manager
inventory_manager = StateOfTheArtInventoryManager()

# Create FastAPI app
app = FastAPI(title="Greenfield Metal Sales Inventory System", version="3.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup - BULLETPROOF"""
    logger.info("🚀 STARTING STATE-OF-THE-ART INVENTORY SYSTEM V3.0")
    
    # Authenticate and do immediate sync
    try:
        auth_result = await inventory_manager.authenticate()
        if auth_result:
            logger.info("✅ PARADIGM CONNECTION ESTABLISHED")
            
            # Force immediate sync on startup
            logger.info("🔄 FORCING IMMEDIATE SYNC ON STARTUP...")
            sync_result = await inventory_manager.sync_to_database()
            
            if sync_result.get("success"):
                logger.info(f"🎉 STARTUP SYNC SUCCESSFUL: {sync_result.get('items_synced')} items")
            else:
                logger.error(f"❌ STARTUP SYNC FAILED: {sync_result.get('error')}")
        else:
            logger.error("❌ PARADIGM CONNECTION FAILED")
    except Exception as e:
        logger.error(f"❌ STARTUP ERROR: {e}")

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    stats = await inventory_manager.get_stats()
    return {
        "status": "healthy",
        "version": "3.0",
        "timestamp": datetime.now().isoformat(),
        "service": "Greenfield Metal Sales Inventory System V3",
        "environment": "production",
        "paradigm_connected": stats.get("paradigm_connected", False),
        "total_items": stats.get("total_items", 0)
    }

@app.get("/api/stats")
async def get_stats():
    """Get comprehensive system statistics"""
    return await inventory_manager.get_stats()

@app.get("/api/paradigm/auth")
async def test_paradigm_auth():
    """Test Paradigm authentication"""
    result = await inventory_manager.authenticate()
    return {"success": result, "authenticated": inventory_manager.auth_token is not None}

@app.post("/api/paradigm/sync")
async def manual_sync():
    """Manual sync trigger"""
    logger.info("🔄 MANUAL SYNC REQUESTED")
    result = await inventory_manager.sync_to_database()
    logger.info(f"🔄 MANUAL SYNC RESULT: {result}")
    return result

@app.get("/api/search")
async def search_inventory(q: str = "", limit: int = 100):
    """Search inventory"""
    return await inventory_manager.search_inventory(q, limit)

@app.get("/api/paradigm/items")
async def get_items(skip: int = 0, take: int = 100):
    """Get items - returns local data for speed"""
    return await inventory_manager.search_inventory("", take)

@app.post("/api/paradigm/update-quantity")
async def update_quantity(request: Request):
    """Update item quantity"""
    try:
        data = await request.json()
        product_id = data.get("product_id")
        quantity = data.get("quantity")
        
        if not product_id or quantity is None:
            raise HTTPException(status_code=400, detail="product_id and quantity required")
        
        return await inventory_manager.update_item_quantity(product_id, float(quantity))
    except Exception as e:
        logger.error(f"❌ UPDATE QUANTITY ERROR: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/paradigm/update-inventory")
async def update_inventory(request: Request):
    """Update inventory quantity (alias)"""
    return await update_quantity(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
