#!/usr/bin/env python3
"""
DEBUG THE SYNC FUNCTION LOCALLY
Find out exactly why the database isn't getting populated
"""

import asyncio
import aiosqlite
import httpx
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paradigm API Configuration
PARADIGM_BASE_URL = "https://greenfieldapi.para-apps.com"
PARADIGM_API_KEY = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
PARADIGM_USERNAME = "web_admin"
PARADIGM_PASSWORD = "ChangeMe#123!"

# Database path
DB_PATH = "debug_inventory.db"

class DebugInventoryManager:
    def __init__(self):
        self.auth_token = None
        self.base_url = PARADIGM_BASE_URL
        self.api_key = PARADIGM_API_KEY
        self.username = PARADIGM_USERNAME
        self.password = PARADIGM_PASSWORD
        
    async def authenticate(self):
        """Authenticate with Paradigm API"""
        try:
            auth_data = {
                "username": self.username,
                "password": self.password
            }
            
            logger.info(f"🔐 Attempting authentication...")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/user/Auth/GetToken",
                    json=auth_data,
                    headers={"X-API-Key": self.api_key, "Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.auth_token = data.get("data")
                    
                    if self.auth_token:
                        logger.info("✅ Authentication successful")
                        return True
                    else:
                        logger.error(f"❌ No token found in response: {data}")
                        return False
                else:
                    logger.error(f"❌ Authentication failed: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    async def get_inventory_items(self, skip: int = 0, take: int = 100):
        """Get inventory items from Paradigm"""
        if not self.auth_token:
            if not await self.authenticate():
                return {"error": "Authentication failed"}
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                headers = {
                    "Authorization": f"Bearer {self.auth_token}",
                    "X-API-Key": self.api_key
                }
                
                logger.info(f"📦 Getting items: skip={skip}, take={take}")
                
                response = await client.get(
                    f"{self.base_url}/api/Items/GetItems/{skip}/{take}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    items = response.json()
                    logger.info(f"✅ Retrieved {len(items)} items from Paradigm")
                    return {"success": True, "items": items, "count": len(items)}
                else:
                    logger.error(f"❌ GetItems failed: {response.status_code} - {response.text}")
                    return {"error": f"API call failed: {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"❌ GetItems error: {e}")
            return {"error": str(e)}
    
    async def sync_to_local_database(self):
        """Sync Paradigm data to local database - DEBUG VERSION"""
        logger.info("🔄 Starting DEBUG sync...")
        
        try:
            # Get items from Paradigm
            logger.info("📦 Getting items from Paradigm...")
            response = await self.get_inventory_items(0, 1000)  # Start with 1000 for debugging
            
            if "error" in response:
                logger.error(f"❌ Failed to get items: {response}")
                return response
            
            items = response.get("items", [])
            logger.info(f"📦 Got {len(items)} items from Paradigm")
            
            if len(items) == 0:
                logger.error("❌ No items received from Paradigm!")
                return {"error": "No items received from Paradigm"}
            
            # Show first item structure
            if items:
                logger.info(f"📦 First item structure: {items[0]}")
            
            # Initialize database
            logger.info("💾 Initializing database...")
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS inventory (
                        product_id TEXT PRIMARY KEY,
                        description TEXT,
                        current_quantity INTEGER,
                        unit_measure TEXT,
                        category TEXT,
                        last_updated TIMESTAMP
                    )
                ''')
                await db.commit()
                logger.info("✅ Database table created/verified")
                
                # Process items
                processed_count = 0
                for item in items:
                    try:
                        product_id = item.get("strProductID")
                        description = item.get("memDescription")
                        quantity = item.get("decUnitsInStock") or 0
                        unit_measure = item.get("strUnitMeasure")
                        category = item.get("strCategory")
                        
                        if product_id:
                            await db.execute('''
                                INSERT OR REPLACE INTO inventory 
                                (product_id, description, current_quantity, unit_measure, category, last_updated)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (product_id, description, quantity, unit_measure, category, datetime.now()))
                            processed_count += 1
                            
                            if processed_count <= 5:  # Log first 5 items
                                logger.info(f"💾 Inserted: {product_id} - {description} - Qty: {quantity}")
                        else:
                            logger.warning(f"⚠️ Item missing product_id: {item}")
                    
                    except Exception as item_error:
                        logger.error(f"❌ Error processing item {item.get('strProductID', 'UNKNOWN')}: {item_error}")
                
                await db.commit()
                logger.info(f"💾 Database commit completed")
                
                # Verify data was inserted
                cursor = await db.execute("SELECT COUNT(*) FROM inventory")
                count = await cursor.fetchone()
                db_count = count[0] if count else 0
                
                logger.info(f"🔍 Database verification: {db_count} items in database")
                
                # Show sample data
                cursor = await db.execute("SELECT * FROM inventory LIMIT 3")
                sample_rows = await cursor.fetchall()
                logger.info(f"📊 Sample data: {sample_rows}")
            
            logger.info(f"✅ Sync completed: {processed_count} items processed, {db_count} in database")
            return {"success": True, "items_synced": processed_count, "database_count": db_count}
            
        except Exception as e:
            logger.error(f"❌ Sync error: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}

async def debug_sync():
    """Run the debug sync process"""
    print("🔥🔥🔥 DEBUGGING SYNC FUNCTION LOCALLY 🔥🔥🔥")
    print("=" * 60)
    
    # Remove old debug database
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"🗑️ Removed old debug database: {DB_PATH}")
    
    manager = DebugInventoryManager()
    
    # Test authentication
    print("\n🔐 Testing authentication...")
    auth_result = await manager.authenticate()
    if not auth_result:
        print("❌ Authentication failed - cannot proceed")
        return
    
    # Test getting items
    print("\n📦 Testing get items...")
    items_result = await manager.get_inventory_items(0, 10)
    if "error" in items_result:
        print(f"❌ Get items failed: {items_result['error']}")
        return
    
    print(f"✅ Got {items_result['count']} items")
    
    # Test sync
    print("\n🔄 Testing sync to database...")
    sync_result = await manager.sync_to_local_database()
    
    if sync_result.get("success"):
        print(f"✅ Sync successful!")
        print(f"📊 Items synced: {sync_result.get('items_synced')}")
        print(f"💾 Database count: {sync_result.get('database_count')}")
        
        # Test local search
        print(f"\n🔍 Testing local database search...")
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM inventory")
            count = await cursor.fetchone()
            print(f"📊 Total items in database: {count[0] if count else 0}")
            
            cursor = await db.execute("SELECT * FROM inventory WHERE product_id LIKE '%COIL%' LIMIT 5")
            coil_items = await cursor.fetchall()
            print(f"🔍 COIL search results: {len(coil_items)} items found")
            for item in coil_items:
                print(f"   - {item[0]}: {item[1]} (Qty: {item[2]})")
        
        print("\n🎉 DEBUG SYNC SUCCESSFUL!")
        return True
    else:
        print(f"❌ Sync failed: {sync_result.get('error')}")
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_sync())
    if success:
        print("\n✅ LOCAL SYNC WORKS - ISSUE IS WITH CLOUD DEPLOYMENT")
    else:
        print("\n❌ LOCAL SYNC ALSO BROKEN - NEED TO FIX SYNC LOGIC")
