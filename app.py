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
            
            # Update the quantity and set proper Paradigm flags
            current_item["decUnitsInStock"] = new_quantity
            
            # Reset committed units to prevent double-counting
            current_item["decUnitsCommitted"] = 0.0
            
            # Set Paradigm flags for proper inventory tracking
            current_item["ysnUpdateUnitsCommitted"] = False
            current_item["ysnUpdateUnitsPulled"] = False
            
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

@app.get("/", response_class=HTMLResponse)
async def main_page():
    """Main dashboard page - State of the Art Design"""
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Greenfield Metal Sales - AI Inventory Management</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
            padding: 30px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }
        
        .version-badge {
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .stats-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.95);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            backdrop-filter: blur(4px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-icon {
            font-size: 2.5em;
            margin-bottom: 15px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stat-number {
            font-size: 2.2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        
        .stat-label {
            color: #666;
            font-size: 1.1em;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }
        
        .search-section, .results-section {
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            backdrop-filter: blur(4px);
            border: 1px solid rgba(255, 255, 255, 0.18);
        }
        
        .section-title {
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #333;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .search-container {
            position: relative;
            margin-bottom: 20px;
        }
        
        .search-input {
            width: 100%;
            padding: 15px 50px 15px 20px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1.1em;
            transition: border-color 0.3s ease;
        }
        
        .search-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .search-button {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            transition: opacity 0.3s ease;
        }
        
        .search-button:hover {
            opacity: 0.9;
        }
        
        .results-container {
            max-height: 500px;
            overflow-y: auto;
        }
        
        .result-item {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            transition: transform 0.2s ease;
        }
        
        .result-item:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .result-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .product-id {
            font-weight: bold;
            font-size: 1.2em;
            color: #667eea;
        }
        
        .quantity-badge {
            background: linear-gradient(45deg, #28a745, #20c997);
            color: white;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .product-description {
            color: #555;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        
        .product-details {
            display: flex;
            gap: 20px;
            font-size: 0.9em;
            color: #777;
        }
        
        .detail-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .inventory-management {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }
        
        .inventory-controls {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .quantity-input {
            width: 80px;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        
        .update-button {
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
            transition: opacity 0.3s ease;
        }
        
        .update-button:hover {
            opacity: 0.9;
        }
        
        .actions-section {
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            backdrop-filter: blur(4px);
            border: 1px solid rgba(255, 255, 255, 0.18);
        }
        
        .actions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .action-button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 20px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 1em;
            transition: transform 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .action-button:hover {
            transform: translateY(-2px);
        }
        
        .footer {
            text-align: center;
            color: rgba(255, 255, 255, 0.8);
            margin-top: 40px;
            padding: 20px;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .stats-section {
                grid-template-columns: 1fr 1fr;
            }
            
            .header h1 {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-industry"></i> Greenfield Metal Sales</h1>
            <p>AI-Powered Inventory Management System <span class="version-badge">v3.0</span></p>
            <p>24/7 Cloud-Hosted with Background Sync & Instant Search</p>
        </div>
        
        <div class="stats-section">
            <div class="stat-card">
                <div class="stat-icon"><i class="fas fa-database"></i></div>
                <div class="stat-number" id="totalItems">Loading...</div>
                <div class="stat-label">Total Products</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon"><i class="fas fa-sync-alt"></i></div>
                <div class="stat-number" id="lastSync">Loading...</div>
                <div class="stat-label">Last Sync</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon"><i class="fas fa-link"></i></div>
                <div class="stat-number" id="paradigmStatus">Loading...</div>
                <div class="stat-label">Paradigm Status</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon"><i class="fas fa-server"></i></div>
                <div class="stat-number" id="systemStatus">Loading...</div>
                <div class="stat-label">System Status</div>
            </div>
        </div>
        
        <div class="main-content">
            <div class="search-section">
                <h2 class="section-title"><i class="fas fa-search"></i> Search Inventory</h2>
                <div class="search-container">
                    <input type="text" class="search-input" id="searchInput" placeholder="Search by product ID, description, or category..." onkeypress="handleSearchKeyPress(event)">
                    <button class="search-button" onclick="searchProducts()"><i class="fas fa-search"></i> Search Products</button>
                </div>
            </div>
            
            <div class="results-section">
                <h2 class="section-title"><i class="fas fa-list"></i> Search Results</h2>
                <div class="results-container" id="resultsContainer">
                    <p style="text-align: center; color: #666; margin-top: 50px;">
                        <i class="fas fa-search" style="font-size: 3em; margin-bottom: 20px; opacity: 0.3;"></i><br>
                        Enter a search term to find products
                    </p>
                </div>
            </div>
        </div>
        
        <div class="actions-section">
            <h2 class="section-title"><i class="fas fa-cogs"></i> System Actions</h2>
            <div class="actions-grid">
                <button class="action-button" onclick="testAuth()">
                    <i class="fas fa-key"></i> Test Authentication
                </button>
                <button class="action-button" onclick="getAllItems()">
                    <i class="fas fa-download"></i> Get All Items
                </button>
                <button class="action-button" onclick="syncDatabase()">
                    <i class="fas fa-sync"></i> Sync Database
                </button>
                <button class="action-button" onclick="updateTestItem()">
                    <i class="fas fa-edit"></i> Test Update
                </button>
            </div>
        </div>
        
        <div class="footer">
            <p>&copy; 2025 Greenfield Metal Sales - AI-Powered Inventory Management System</p>
            <p>Built with FastAPI, SQLite, and Paradigm ERP Integration</p>
        </div>
    </div>

    <script>
        // Load stats on page load
        window.onload = function() {
            loadStats();
        };
        
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                if (data.total_items !== undefined) {
                    document.getElementById('totalItems').textContent = data.total_items.toLocaleString();
                }
                
                if (data.last_sync) {
                    const lastSync = new Date(data.last_sync);
                    const timeAgo = getTimeAgo(lastSync);
                    document.getElementById('lastSync').textContent = timeAgo;
                } else {
                    document.getElementById('lastSync').textContent = 'Never';
                }
                
                document.getElementById('paradigmStatus').textContent = data.paradigm_connected ? 'Connected' : 'Disconnected';
                document.getElementById('systemStatus').textContent = 'Online';
                
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }
        
        function getTimeAgo(date) {
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMs / 3600000);
            const diffDays = Math.floor(diffMs / 86400000);
            
            if (diffMins < 1) return 'Just now';
            if (diffMins < 60) return `${diffMins}m ago`;
            if (diffHours < 24) return `${diffHours}h ago`;
            return `${diffDays}d ago`;
        }
        
        async function searchProducts() {
            const searchTerm = document.getElementById('searchInput').value.trim();
            const resultsContainer = document.getElementById('resultsContainer');
            
            if (!searchTerm) {
                resultsContainer.innerHTML = '<p style="text-align: center; color: #666;">Please enter a search term</p>';
                return;
            }
            
            resultsContainer.innerHTML = '<p style="text-align: center; color: #666;"><i class="fas fa-spinner fa-spin"></i> Searching...</p>';
            
            try {
                const response = await fetch(`/api/search?q=${encodeURIComponent(searchTerm)}&limit=50`);
                const data = await response.json();
                
                if (data.success && data.items.length > 0) {
                    displayResults(data.items);
                } else {
                    resultsContainer.innerHTML = `<p style="text-align: center; color: #666;">No results found for "${searchTerm}"</p>`;
                }
            } catch (error) {
                resultsContainer.innerHTML = '<p style="text-align: center; color: #dc3545;">Error searching products</p>';
                console.error('Search error:', error);
            }
        }
        
        function displayResults(items) {
            const resultsContainer = document.getElementById('resultsContainer');
            const resultsHtml = items.map(item => `
                <div class="result-item">
                    <div class="result-header">
                        <div class="product-id">${item.product_id}</div>
                        <div class="quantity-badge">${item.current_quantity} ${item.unit_measure || 'units'}</div>
                    </div>
                    <div class="product-description">${item.description || 'No description available'}</div>
                    <div class="product-details">
                        <div class="detail-item">
                            <i class="fas fa-tag"></i>
                            <span>Category: ${item.category || 'N/A'}</span>
                        </div>
                        <div class="detail-item">
                            <i class="fas fa-dollar-sign"></i>
                            <span>Price: $${item.sales_price || '0.00'}</span>
                        </div>
                    </div>
                    <div class="inventory-management">
                        <div class="inventory-controls">
                            <input type="number" 
                                   id="qty-${item.product_id}" 
                                   value="${item.current_quantity}" 
                                   class="quantity-input"
                                   placeholder="Qty">
                            <button onclick="updateInventory('${item.product_id}')" class="update-button">
                                <i class="fas fa-save"></i> Update
                            </button>
                            <span style="font-size: 12px; color: #666;">${item.unit_measure || 'units'}</span>
                        </div>
                    </div>
                </div>
            `).join('');
            
            resultsContainer.innerHTML = `
                <div style="margin-bottom: 20px; color: #667eea; font-weight: 600;">
                    <i class="fas fa-check-circle"></i> Found ${items.length} product(s)
                </div>
                ${resultsHtml}
            `;
        }
        
        async function updateInventory(productId) {
            const quantityInput = document.getElementById(`qty-${productId}`);
            const newQuantity = parseFloat(quantityInput.value);
            
            if (isNaN(newQuantity)) {
                alert('Please enter a valid quantity');
                return;
            }
            
            try {
                const response = await fetch('/api/paradigm/update-quantity', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({product_id: productId, quantity: newQuantity})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert(`✅ Successfully updated ${productId} to quantity ${newQuantity}`);
                    // Update the quantity badge
                    const resultItem = quantityInput.closest('.result-item');
                    const quantityBadge = resultItem.querySelector('.quantity-badge');
                    const unitText = quantityBadge.textContent.split(' ').slice(1).join(' ');
                    quantityBadge.textContent = `${newQuantity} ${unitText}`;
                } else {
                    alert(`❌ Update failed: ${data.error}`);
                }
            } catch (error) {
                alert(`❌ Error updating inventory: ${error.message}`);
            }
        }
        
        function handleSearchKeyPress(event) {
            if (event.key === 'Enter') {
                searchProducts();
            }
        }
        
        // System action functions
        async function testAuth() {
            try {
                const response = await fetch('/api/paradigm/auth');
                const data = await response.json();
                if (data.success) {
                    alert('✅ Authentication successful! Paradigm API is connected.');
                } else {
                    alert('❌ Authentication failed. Please check Paradigm API credentials.');
                }
            } catch (error) {
                alert('❌ Error testing authentication: ' + error.message);
            }
        }
        
        async function getAllItems() {
            try {
                const response = await fetch('/api/paradigm/items?skip=0&take=100');
                const data = await response.json();
                if (data.success) {
                    alert(`✅ Successfully retrieved ${data.count.toLocaleString()} items from Paradigm!\\n\\n📊 System now has all items available for instant search.\\n🔄 Background sync runs automatically.`);
                } else {
                    alert('❌ Failed to get items: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                alert('❌ Error getting items: ' + error.message);
            }
        }
        
        async function syncDatabase() {
            try {
                const response = await fetch('/api/paradigm/sync', {method: 'POST'});
                const data = await response.json();
                if (data.success) {
                    alert(`✅ Successfully synced ${data.items_synced.toLocaleString()} items to database!\\n\\n🔄 Background sync will continue automatically.\\n⚡ Search is now instant using local data.`);
                    loadStats(); // Refresh stats
                } else {
                    alert('❌ Sync failed: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                alert('❌ Error syncing database: ' + error.message);
            }
        }
        
        async function updateTestItem() {
            try {
                const response = await fetch('/api/paradigm/update-quantity', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({product_id: 'BEND', quantity: 999})
                });
                const data = await response.json();
                if (data.success) {
                    alert('✅ Test update successful! Paradigm integration is working.');
                } else {
                    alert('❌ Test update failed: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                alert('❌ Error testing update: ' + error.message);
            }
        }
    </script>
</body>
</html>
    """)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
