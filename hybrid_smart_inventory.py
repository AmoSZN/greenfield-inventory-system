#!/usr/bin/env python3
"""
Hybrid Smart Inventory System for Greenfield Metal Sales
Handles all 38,998 items with intelligent search, caching, and learning
Production-ready implementation with professional features
"""

from fastapi import FastAPI, Form, Request, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import httpx
import uvicorn
from datetime import datetime, timedelta
import json
import asyncio
import os
from typing import List, Dict, Optional, Set, Tuple
import logging
from collections import defaultdict
import re
import csv
import io
from pathlib import Path
import sqlite3
import aiosqlite
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create necessary directories
Path("data").mkdir(exist_ok=True)
Path("cache").mkdir(exist_ok=True)
Path("exports").mkdir(exist_ok=True)

app = FastAPI(title="Greenfield Metal Sales - Hybrid Smart Inventory System")

# Paradigm ERP Configuration
PARADIGM_BASE_URL = "https://greenfieldapi.para-apps.com"
PARADIGM_API_KEY = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
PARADIGM_USERNAME = "web_admin"
PARADIGM_PASSWORD = "ChangeMe#123!"

# Database configuration
DB_PATH = "data/smart_inventory.db"

# System state
system_state = {
    "total_items_capacity": 38998,
    "items_discovered": 0,
    "items_cached": 0,
    "last_import": None,
    "system_health": "operational",
    "cache_hits": 0,
    "cache_misses": 0,
    "api_calls": 0,
    "startup_time": datetime.now()
}

class SmartInventoryDatabase:
    """Async SQLite database for inventory management"""
    
    @staticmethod
    async def init_db():
        """Initialize database with tables"""
        async with aiosqlite.connect(DB_PATH) as db:
            # Items table - stores all known items
            await db.execute('''
                CREATE TABLE IF NOT EXISTS items (
                    product_id TEXT PRIMARY KEY,
                    description TEXT,
                    category TEXT,
                    subcategory TEXT,
                    current_quantity INTEGER,
                    last_updated TIMESTAMP,
                    times_accessed INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP,
                    is_verified BOOLEAN DEFAULT 0,
                    custom_fields TEXT
                )
            ''')
            
            # Search patterns table - learns from user searches
            await db.execute('''
                CREATE TABLE IF NOT EXISTS search_patterns (
                    pattern TEXT PRIMARY KEY,
                    frequency INTEGER DEFAULT 1,
                    last_used TIMESTAMP
                )
            ''')
            
            # Update history table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS update_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT,
                    update_type TEXT,
                    old_value TEXT,
                    new_value TEXT,
                    updated_by TEXT,
                    updated_at TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES items (product_id)
                )
            ''')
            
            # Create indexes for performance
            await db.execute('CREATE INDEX IF NOT EXISTS idx_description ON items(description)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_last_accessed ON items(last_accessed DESC)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_times_accessed ON items(times_accessed DESC)')
            
            await db.commit()
            logger.info("Database initialized successfully")

class HybridInventoryManager:
    """Advanced inventory manager with smart features"""
    
    def __init__(self):
        self.auth_token = None
        self.token_expiry = None
        self.search_cache = {}  # In-memory cache for fast searches
        self.pattern_matcher = PatternMatcher()
    
    async def authenticate(self) -> bool:
        """Authenticate with Paradigm ERP"""
        try:
            if self.auth_token and self.token_expiry and datetime.now() < self.token_expiry:
                return True
            
            auth_payload = {
                "userName": PARADIGM_USERNAME,
                "password": PARADIGM_PASSWORD
            }
            
            headers = {
                "x-api-key": PARADIGM_API_KEY,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{PARADIGM_BASE_URL}/api/user/Auth/GetToken",
                    headers=headers,
                    json=auth_payload
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    if token_data.get("isLoginValid"):
                        self.auth_token = token_data.get("data")
                        self.token_expiry = datetime.now() + timedelta(hours=8)
                        logger.info("Authentication successful")
                        return True
                
                logger.error("Authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    async def smart_search(self, query: str, limit: int = 50) -> List[Dict]:
        """Intelligent search with caching and pattern learning"""
        query = query.upper().strip()
        
        # Record search pattern
        await self.record_search_pattern(query)
        
        # Check cache first
        if query in self.search_cache:
            system_state["cache_hits"] += 1
            return self.search_cache[query][:limit]
        
        system_state["cache_misses"] += 1
        
        # Search database
        results = []
        async with aiosqlite.connect(DB_PATH) as db:
            # Exact match first
            cursor = await db.execute(
                '''SELECT product_id, description, category, times_accessed 
                   FROM items 
                   WHERE product_id = ? 
                   LIMIT ?''',
                (query, limit)
            )
            exact_matches = await cursor.fetchall()
            
            # Prefix match
            cursor = await db.execute(
                '''SELECT product_id, description, category, times_accessed 
                   FROM items 
                   WHERE product_id LIKE ? 
                   ORDER BY times_accessed DESC, product_id 
                   LIMIT ?''',
                (f"{query}%", limit)
            )
            prefix_matches = await cursor.fetchall()
            
            # Description match
            cursor = await db.execute(
                '''SELECT product_id, description, category, times_accessed 
                   FROM items 
                   WHERE description LIKE ? 
                   ORDER BY times_accessed DESC, product_id 
                   LIMIT ?''',
                (f"%{query}%", limit)
            )
            desc_matches = await cursor.fetchall()
            
            # Combine results, removing duplicates
            seen = set()
            for matches in [exact_matches, prefix_matches, desc_matches]:
                for row in matches:
                    if row[0] not in seen:
                        results.append({
                            "product_id": row[0],
                            "description": row[1],
                            "category": row[2],
                            "relevance": row[3]  # times_accessed as relevance
                        })
                        seen.add(row[0])
        
        # Cache results
        self.search_cache[query] = results
        
        # If no results, try pattern-based suggestions
        if not results:
            suggestions = self.pattern_matcher.suggest_products(query)
            for suggestion in suggestions[:limit]:
                results.append({
                    "product_id": suggestion,
                    "description": "Suggested based on pattern",
                    "category": "Pattern Match",
                    "relevance": 0
                })
        
        return results[:limit]
    
    async def validate_and_add_item(self, product_id: str) -> Tuple[bool, Dict]:
        """Validate item exists in Paradigm and add to database"""
        if not await self.authenticate():
            return False, {"error": "Authentication failed"}
        
        try:
            # Try to update with minimal data to check existence
            test_payload = {
                "strProductID": product_id,
                "dtmLastModified": datetime.now().isoformat()
            }
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "x-api-key": PARADIGM_API_KEY,
                "Content-Type": "application/json"
            }
            
            system_state["api_calls"] += 1
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.put(
                    f"{PARADIGM_BASE_URL}/api/Items/UpdateItem?excludeNullValues=true",
                    headers=headers,
                    json=test_payload
                )
                
                if response.status_code == 200:
                    # Item exists! Extract data from response
                    item_data = response.json()
                    
                    # Add to database
                    await self.add_item_to_db(product_id, item_data)
                    
                    return True, {
                        "product_id": product_id,
                        "status": "verified",
                        "data": item_data
                    }
                else:
                    return False, {
                        "product_id": product_id,
                        "status": "not_found",
                        "error": f"Item not found in Paradigm ERP"
                    }
                    
        except Exception as e:
            logger.error(f"Validation error for {product_id}: {str(e)}")
            return False, {"error": str(e)}
    
    async def add_item_to_db(self, product_id: str, item_data: Dict = None):
        """Add or update item in database"""
        async with aiosqlite.connect(DB_PATH) as db:
            if item_data:
                await db.execute('''
                    INSERT OR REPLACE INTO items 
                    (product_id, description, category, subcategory, current_quantity, 
                     last_updated, is_verified, custom_fields)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    product_id,
                    item_data.get("memDescription", ""),
                    item_data.get("strCategory", ""),
                    item_data.get("strSubcategory", ""),
                    item_data.get("decUnitsInStock", 0),
                    datetime.now(),
                    1,
                    json.dumps(item_data)
                ))
            else:
                # Minimal entry for unverified item
                await db.execute('''
                    INSERT OR IGNORE INTO items (product_id, last_updated, is_verified)
                    VALUES (?, ?, ?)
                ''', (product_id, datetime.now(), 0))
            
            await db.commit()
            system_state["items_discovered"] += 1
    
    async def update_item(self, product_id: str, updates: Dict) -> Tuple[bool, Dict]:
        """Update item in Paradigm ERP"""
        if not await self.authenticate():
            return False, {"error": "Authentication failed"}
        
        try:
            # Build update payload
            update_payload = {
                "strProductID": product_id,
                "dtmLastModified": datetime.now().isoformat()
            }
            
            # Add optional fields
            if "quantity" in updates and updates["quantity"]:
                update_payload["decUnitsInStock"] = float(updates["quantity"])
            
            if "description" in updates and updates["description"]:
                update_payload["memDescription"] = updates["description"]
                
            if "purchase_description" in updates and updates["purchase_description"]:
                update_payload["memPurchaseDescription"] = updates["purchase_description"]
                
            if "notes" in updates and updates["notes"]:
                update_payload["strNotes"] = updates["notes"]
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "x-api-key": PARADIGM_API_KEY,
                "Content-Type": "application/json"
            }
            
            system_state["api_calls"] += 1
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.put(
                    f"{PARADIGM_BASE_URL}/api/Items/UpdateItem?excludeNullValues=true",
                    headers=headers,
                    json=update_payload
                )
                
                if response.status_code == 200:
                    # Update successful
                    item_data = response.json()
                    
                    # Update database
                    await self.add_item_to_db(product_id, item_data)
                    
                    # Record update history
                    await self.record_update_history(product_id, updates)
                    
                    # Update access count
                    await self.update_access_count(product_id)
                    
                    return True, {
                        "success": True,
                        "product_id": product_id,
                        "updates": updates,
                        "response": item_data
                    }
                else:
                    return False, {
                        "success": False,
                        "error": f"Update failed: {response.status_code}",
                        "details": response.text
                    }
                    
        except Exception as e:
            logger.error(f"Update error for {product_id}: {str(e)}")
            return False, {"error": str(e)}
    
    async def record_search_pattern(self, pattern: str):
        """Record search patterns for learning"""
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('''
                INSERT INTO search_patterns (pattern, frequency, last_used)
                VALUES (?, 1, ?)
                ON CONFLICT(pattern) DO UPDATE SET
                frequency = frequency + 1,
                last_used = ?
            ''', (pattern, datetime.now(), datetime.now()))
            await db.commit()
    
    async def record_update_history(self, product_id: str, updates: Dict):
        """Record update history for audit trail"""
        async with aiosqlite.connect(DB_PATH) as db:
            for field, value in updates.items():
                await db.execute('''
                    INSERT INTO update_history 
                    (product_id, update_type, new_value, updated_by, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (product_id, field, str(value), "web_user", datetime.now()))
            await db.commit()
    
    async def update_access_count(self, product_id: str):
        """Update access count for frequently used items"""
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('''
                UPDATE items 
                SET times_accessed = times_accessed + 1,
                    last_accessed = ?
                WHERE product_id = ?
            ''', (datetime.now(), product_id))
            await db.commit()
    
    async def import_csv(self, file_content: bytes) -> Dict:
        """Import items from CSV file"""
        try:
            # Parse CSV
            text_content = file_content.decode('utf-8-sig')  # Handle BOM
            csv_reader = csv.DictReader(io.StringIO(text_content))
            
            imported = 0
            errors = []
            
            async with aiosqlite.connect(DB_PATH) as db:
                for row in csv_reader:
                    try:
                        # Map CSV fields to database (adjust based on actual CSV format)
                        product_id = row.get('Product ID', row.get('strProductID', '')).strip()
                        
                        if product_id:
                            await db.execute('''
                                INSERT OR REPLACE INTO items 
                                (product_id, description, category, subcategory, 
                                 current_quantity, last_updated, is_verified)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                product_id,
                                row.get('Description', row.get('memDescription', '')),
                                row.get('Category', row.get('strCategory', '')),
                                row.get('Subcategory', row.get('strSubcategory', '')),
                                float(row.get('Quantity', row.get('decUnitsInStock', 0))),
                                datetime.now(),
                                1  # Mark as verified since it's from export
                            ))
                            imported += 1
                        else:
                            errors.append(f"Missing Product ID in row: {row}")
                            
                    except Exception as e:
                        errors.append(f"Error processing row {row}: {str(e)}")
                
                await db.commit()
            
            system_state["items_discovered"] = imported
            system_state["last_import"] = datetime.now()
            
            return {
                "success": True,
                "imported": imported,
                "errors": errors,
                "message": f"Successfully imported {imported} items"
            }
            
        except Exception as e:
            logger.error(f"CSV import error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to import CSV file"
            }
    
    async def get_frequent_items(self, limit: int = 20) -> List[Dict]:
        """Get frequently accessed items"""
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute('''
                SELECT product_id, description, category, times_accessed, last_accessed
                FROM items
                WHERE times_accessed > 0
                ORDER BY times_accessed DESC, last_accessed DESC
                LIMIT ?
            ''', (limit,))
            
            rows = await cursor.fetchall()
            
            return [
                {
                    "product_id": row[0],
                    "description": row[1],
                    "category": row[2],
                    "times_accessed": row[3],
                    "last_accessed": row[4]
                }
                for row in rows
            ]
    
    async def get_recent_updates(self, limit: int = 10) -> List[Dict]:
        """Get recent update history"""
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute('''
                SELECT h.product_id, h.update_type, h.new_value, h.updated_at, i.description
                FROM update_history h
                LEFT JOIN items i ON h.product_id = i.product_id
                ORDER BY h.updated_at DESC
                LIMIT ?
            ''', (limit,))
            
            rows = await cursor.fetchall()
            
            return [
                {
                    "product_id": row[0],
                    "update_type": row[1],
                    "new_value": row[2],
                    "updated_at": row[3],
                    "description": row[4]
                }
                for row in rows
            ]
    
    async def export_database(self) -> bytes:
        """Export database to CSV for backup"""
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute('''
                SELECT product_id, description, category, subcategory, 
                       current_quantity, last_updated, times_accessed
                FROM items
                ORDER BY product_id
            ''')
            
            rows = await cursor.fetchall()
            
            # Create CSV
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow([
                'Product ID', 'Description', 'Category', 'Subcategory',
                'Current Quantity', 'Last Updated', 'Times Accessed'
            ])
            
            # Data
            for row in rows:
                writer.writerow(row)
            
            return output.getvalue().encode('utf-8')

class PatternMatcher:
    """Intelligent pattern matching for product suggestions"""
    
    def __init__(self):
        self.known_patterns = {
            'series': ['1010', '1015', '1020', '1025', '1030'],
            'suffixes': ['AG', 'ARW', 'AW', 'B', 'BER', 'BS', 'BUC', 'BUR', 'BW', 
                        'CB', 'CG', 'CR', 'DB', 'DR', 'EV', 'G', 'GB', 'HB', 'I', 
                        'IG', 'KB', 'LS', 'MB', 'OB', 'OG', 'PG', 'R', 'RR', 'ST', 
                        'T', 'TAP']
        }
    
    def suggest_products(self, partial: str) -> List[str]:
        """Generate product suggestions based on partial input"""
        suggestions = []
        partial = partial.upper()
        
        # Check if it matches a series pattern
        for series in self.known_patterns['series']:
            if series.startswith(partial):
                # Suggest common suffixes for this series
                for suffix in self.known_patterns['suffixes'][:10]:  # Top 10 suffixes
                    suggestions.append(f"{series}{suffix}")
        
        # Check if it's a complete series needing suffix
        if partial in self.known_patterns['series']:
            for suffix in self.known_patterns['suffixes']:
                suggestions.append(f"{partial}{suffix}")
        
        # Check partial suffix matches
        if len(partial) > 4:
            base = partial[:4]
            suffix_part = partial[4:]
            if base in self.known_patterns['series']:
                for suffix in self.known_patterns['suffixes']:
                    if suffix.startswith(suffix_part):
                        suggestions.append(f"{base}{suffix}")
        
        return suggestions[:20]  # Return top 20 suggestions

# Initialize manager
inventory_manager = HybridInventoryManager()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    await SmartInventoryDatabase.init_db()
    logger.info("Hybrid Smart Inventory System started")

# HTML Templates
def get_main_interface():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Greenfield Metal Sales - Smart Inventory System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            color: #2c3e50;
        }
        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 1.5rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header h1 {
            font-size: 2rem;
            font-weight: 300;
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        .header .subtitle {
            font-size: 0.9rem;
            opacity: 0.9;
            margin-top: 0.5rem;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            text-align: center;
            transition: transform 0.2s;
        }
        .stat-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #2a5298;
        }
        .stat-label {
            color: #7f8c8d;
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }
        @media (max-width: 768px) {
            .main-grid { grid-template-columns: 1fr; }
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 2rem;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .card h2 {
            color: #2c3e50;
            margin-bottom: 1.5rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .search-container {
            position: relative;
            margin-bottom: 1rem;
        }
        input[type="text"], input[type="number"], textarea, select {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.2s;
        }
        input[type="text"]:focus, input[type="number"]:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #2a5298;
        }
        .search-results {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 2px solid #e0e0e0;
            border-top: none;
            border-radius: 0 0 8px 8px;
            max-height: 300px;
            overflow-y: auto;
            display: none;
            z-index: 1000;
        }
        .search-result {
            padding: 0.75rem;
            cursor: pointer;
            border-bottom: 1px solid #f0f0f0;
            transition: background 0.2s;
        }
        .search-result:hover {
            background: #f8f9fa;
        }
        .search-result .product-id {
            font-weight: bold;
            color: #2a5298;
        }
        .search-result .description {
            font-size: 0.85rem;
            color: #7f8c8d;
        }
        .form-group {
            margin-bottom: 1.5rem;
        }
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            color: #2c3e50;
            font-weight: 500;
        }
        .button-group {
            display: flex;
            gap: 1rem;
            margin-top: 1.5rem;
        }
        button {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.2s;
            font-weight: 500;
        }
        .btn-primary {
            background: #2a5298;
            color: white;
        }
        .btn-primary:hover {
            background: #1e3c72;
        }
        .btn-secondary {
            background: #95a5a6;
            color: white;
        }
        .btn-secondary:hover {
            background: #7f8c8d;
        }
        .btn-success {
            background: #27ae60;
            color: white;
        }
        .btn-success:hover {
            background: #229954;
        }
        .frequent-items {
            display: grid;
            gap: 0.5rem;
            max-height: 400px;
            overflow-y: auto;
        }
        .frequent-item {
            padding: 0.75rem;
            background: #f8f9fa;
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.2s;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .frequent-item:hover {
            background: #e9ecef;
        }
        .frequent-item .usage {
            font-size: 0.85rem;
            color: #7f8c8d;
        }
        .upload-area {
            border: 2px dashed #e0e0e0;
            border-radius: 8px;
            padding: 2rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
        }
        .upload-area:hover {
            border-color: #2a5298;
            background: #f8f9fa;
        }
        .upload-area.dragover {
            border-color: #2a5298;
            background: #e3f2fd;
        }
        .recent-updates {
            max-height: 300px;
            overflow-y: auto;
        }
        .update-item {
            padding: 0.75rem;
            border-bottom: 1px solid #f0f0f0;
            font-size: 0.9rem;
        }
        .update-item:last-child {
            border-bottom: none;
        }
        .update-time {
            color: #7f8c8d;
            font-size: 0.8rem;
        }
        .alert {
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-radius: 50%;
            border-top: 3px solid #2a5298;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .tab-container {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
            border-bottom: 2px solid #e0e0e0;
        }
        .tab {
            padding: 1rem 1.5rem;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.2s;
            color: #7f8c8d;
        }
        .tab:hover {
            color: #2c3e50;
        }
        .tab.active {
            color: #2a5298;
            border-bottom-color: #2a5298;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>
            🏭 Greenfield Metal Sales
            <span style="font-size: 0.8em; opacity: 0.8;">Smart Inventory System</span>
        </h1>
        <div class="subtitle">
            Intelligent management for 38,998 inventory items with real-time Paradigm ERP integration
        </div>
    </div>

    <div class="container">
        <!-- Statistics -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">38,998</div>
                <div class="stat-label">Total Capacity</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="items-discovered">0</div>
                <div class="stat-label">Items Discovered</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="cache-hit-rate">0%</div>
                <div class="stat-label">Cache Hit Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="api-calls">0</div>
                <div class="stat-label">API Calls Today</div>
            </div>
        </div>

        <!-- Tab Navigation -->
        <div class="tab-container">
            <div class="tab active" onclick="switchTab('update')">📦 Update Inventory</div>
            <div class="tab" onclick="switchTab('import')">📤 Import/Export</div>
            <div class="tab" onclick="switchTab('analytics')">📊 Analytics</div>
        </div>

        <!-- Update Tab -->
        <div id="update-tab" class="tab-content active">
            <div class="main-grid">
                <!-- Smart Search and Update -->
                <div class="card">
                    <h2>🔍 Smart Product Search & Update</h2>
                    
                    <div class="form-group">
                        <label>Product ID Search</label>
                        <div class="search-container">
                            <input type="text" id="product-search" placeholder="Type any Product ID (e.g., 1030G, 1025AW)" 
                                   oninput="performSmartSearch(this.value)" autocomplete="off">
                            <div id="search-results" class="search-results"></div>
                        </div>
                    </div>

                    <div id="update-form" style="display: none;">
                        <div class="form-group">
                            <label>Selected Product</label>
                            <input type="text" id="selected-product" readonly style="background: #f8f9fa;">
                        </div>

                        <div class="form-group">
                            <label>New Quantity</label>
                            <input type="number" id="new-quantity" placeholder="Leave blank to skip">
                        </div>

                        <div class="form-group">
                            <label>Description</label>
                            <textarea id="new-description" rows="2" placeholder="Leave blank to skip"></textarea>
                        </div>

                        <div class="form-group">
                            <label>Notes</label>
                            <textarea id="new-notes" rows="2" placeholder="Leave blank to skip"></textarea>
                        </div>

                        <div class="button-group">
                            <button class="btn-primary" onclick="updateInventory()">
                                Update Inventory
                            </button>
                            <button class="btn-secondary" onclick="clearUpdateForm()">
                                Clear
                            </button>
                        </div>
                    </div>

                    <div id="result-message"></div>
                </div>

                <!-- Frequently Used Items -->
                <div class="card">
                    <h2>⭐ Frequently Used Items</h2>
                    <div id="frequent-items" class="frequent-items">
                        <div style="text-align: center; color: #7f8c8d; padding: 2rem;">
                            Start searching to build your frequently used items list
                        </div>
                    </div>
                </div>
            </div>

            <!-- Recent Updates -->
            <div class="card">
                <h2>🕐 Recent Updates</h2>
                <div id="recent-updates" class="recent-updates">
                    <div style="text-align: center; color: #7f8c8d; padding: 2rem;">
                        No recent updates yet
                    </div>
                </div>
            </div>
        </div>

        <!-- Import/Export Tab -->
        <div id="import-tab" class="tab-content">
            <div class="main-grid">
                <!-- CSV Import -->
                <div class="card">
                    <h2>📤 Import from CSV</h2>
                    <p style="margin-bottom: 1rem; color: #7f8c8d;">
                        Import your complete inventory list from Paradigm ERP export
                    </p>
                    
                    <div class="upload-area" id="upload-area" 
                         onclick="document.getElementById('csv-file').click()"
                         ondrop="handleDrop(event)" 
                         ondragover="handleDragOver(event)"
                         ondragleave="handleDragLeave(event)">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">📁</div>
                        <div>Click to browse or drag & drop your CSV file here</div>
                        <div style="font-size: 0.85rem; color: #7f8c8d; margin-top: 0.5rem;">
                            Supports exports from Paradigm ERP
                        </div>
                    </div>
                    
                    <input type="file" id="csv-file" accept=".csv" style="display: none;" 
                           onchange="handleFileSelect(event)">
                    
                    <div id="import-result"></div>
                </div>

                <!-- Export Database -->
                <div class="card">
                    <h2>💾 Export Database</h2>
                    <p style="margin-bottom: 1rem; color: #7f8c8d;">
                        Export your discovered items for backup or analysis
                    </p>
                    
                    <button class="btn-success" onclick="exportDatabase()">
                        Download CSV Export
                    </button>
                    
                    <div style="margin-top: 2rem;">
                        <h3 style="margin-bottom: 1rem;">📊 Export Statistics</h3>
                        <div id="export-stats">
                            Loading statistics...
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Analytics Tab -->
        <div id="analytics-tab" class="tab-content">
            <div class="card">
                <h2>📊 System Analytics</h2>
                <div id="analytics-content">
                    Loading analytics...
                </div>
            </div>
        </div>
    </div>

    <script>
        let searchTimeout;
        let selectedProduct = null;

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            updateStats();
            loadFrequentItems();
            loadRecentUpdates();
            setInterval(updateStats, 30000); // Update stats every 30 seconds
        });

        // Tab switching
        function switchTab(tabName) {
            // Update tab buttons
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            event.target.classList.add('active');

            // Update tab content
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(tabName + '-tab').classList.add('active');

            // Load tab-specific content
            if (tabName === 'analytics') {
                loadAnalytics();
            } else if (tabName === 'import') {
                loadExportStats();
            }
        }

        // Smart search with debouncing
        function performSmartSearch(query) {
            clearTimeout(searchTimeout);
            const resultsDiv = document.getElementById('search-results');
            
            if (query.length < 2) {
                resultsDiv.style.display = 'none';
                return;
            }

            searchTimeout = setTimeout(async () => {
                try {
                    const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                    const results = await response.json();
                    
                    if (results.length > 0) {
                        resultsDiv.innerHTML = results.map(item => `
                            <div class="search-result" onclick="selectProduct('${item.product_id}')">
                                <div class="product-id">${item.product_id}</div>
                                <div class="description">${item.description || 'No description'}</div>
                            </div>
                        `).join('');
                        resultsDiv.style.display = 'block';
                    } else {
                        resultsDiv.innerHTML = `
                            <div class="search-result" onclick="addNewProduct('${query.toUpperCase()}')">
                                <div class="product-id">Add "${query.toUpperCase()}" as new product</div>
                                <div class="description">Click to validate and add to system</div>
                            </div>
                        `;
                        resultsDiv.style.display = 'block';
                    }
                } catch (error) {
                    console.error('Search error:', error);
                }
            }, 300);
        }

        // Select product from search
        function selectProduct(productId) {
            selectedProduct = productId;
            document.getElementById('selected-product').value = productId;
            document.getElementById('product-search').value = productId;
            document.getElementById('search-results').style.display = 'none';
            document.getElementById('update-form').style.display = 'block';
        }

        // Add new product
        async function addNewProduct(productId) {
            const resultsDiv = document.getElementById('search-results');
            resultsDiv.innerHTML = '<div class="search-result"><div class="loading"></div> Validating product...</div>';
            
            try {
                const response = await fetch('/api/validate-product', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ product_id: productId })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    selectProduct(productId);
                    showMessage('success', `Product ${productId} validated and added to system!`);
                } else {
                    showMessage('error', result.error || 'Product not found in Paradigm ERP');
                    resultsDiv.style.display = 'none';
                }
            } catch (error) {
                showMessage('error', 'Failed to validate product');
                resultsDiv.style.display = 'none';
            }
        }

        // Update inventory
        async function updateInventory() {
            if (!selectedProduct) {
                showMessage('error', 'Please select a product first');
                return;
            }

            const updates = {};
            const quantity = document.getElementById('new-quantity').value;
            const description = document.getElementById('new-description').value;
            const notes = document.getElementById('new-notes').value;

            if (quantity) updates.quantity = quantity;
            if (description) updates.description = description;
            if (notes) updates.notes = notes;

            if (Object.keys(updates).length === 0) {
                showMessage('error', 'Please enter at least one field to update');
                return;
            }

            // Show loading
            const button = event.target;
            const originalText = button.innerHTML;
            button.innerHTML = '<span class="loading"></span> Updating...';
            button.disabled = true;

            try {
                const response = await fetch('/api/update-inventory', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        product_id: selectedProduct,
                        updates: updates
                    })
                });

                const result = await response.json();
                
                if (result.success) {
                    showMessage('success', `Successfully updated ${selectedProduct}`);
                    clearUpdateForm();
                    loadRecentUpdates();
                    loadFrequentItems();
                } else {
                    showMessage('error', result.error || 'Update failed');
                }
            } catch (error) {
                showMessage('error', 'Failed to update inventory');
            } finally {
                button.innerHTML = originalText;
                button.disabled = false;
            }
        }

        // Clear update form
        function clearUpdateForm() {
            document.getElementById('product-search').value = '';
            document.getElementById('selected-product').value = '';
            document.getElementById('new-quantity').value = '';
            document.getElementById('new-description').value = '';
            document.getElementById('new-notes').value = '';
            document.getElementById('update-form').style.display = 'none';
            selectedProduct = null;
        }

        // Show message
        function showMessage(type, message) {
            const messageDiv = document.getElementById('result-message');
            messageDiv.className = `alert alert-${type}`;
            messageDiv.textContent = message;
            messageDiv.style.display = 'block';
            
            setTimeout(() => {
                messageDiv.style.display = 'none';
            }, 5000);
        }

        // Update statistics
        async function updateStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                document.getElementById('items-discovered').textContent = stats.items_discovered.toLocaleString();
                
                const hitRate = stats.cache_hits + stats.cache_misses > 0 
                    ? Math.round((stats.cache_hits / (stats.cache_hits + stats.cache_misses)) * 100)
                    : 0;
                document.getElementById('cache-hit-rate').textContent = hitRate + '%';
                
                document.getElementById('api-calls').textContent = stats.api_calls.toLocaleString();
            } catch (error) {
                console.error('Failed to update stats:', error);
            }
        }

        // Load frequent items
        async function loadFrequentItems() {
            try {
                const response = await fetch('/api/frequent-items');
                const items = await response.json();
                
                const container = document.getElementById('frequent-items');
                if (items.length > 0) {
                    container.innerHTML = items.map(item => `
                        <div class="frequent-item" onclick="selectProduct('${item.product_id}')">
                            <div>
                                <strong>${item.product_id}</strong>
                                <div style="font-size: 0.85rem; color: #7f8c8d;">
                                    ${item.description || 'No description'}
                                </div>
                            </div>
                            <div class="usage">Used ${item.times_accessed}x</div>
                        </div>
                    `).join('');
                }
            } catch (error) {
                console.error('Failed to load frequent items:', error);
            }
        }

        // Load recent updates
        async function loadRecentUpdates() {
            try {
                const response = await fetch('/api/recent-updates');
                const updates = await response.json();
                
                const container = document.getElementById('recent-updates');
                if (updates.length > 0) {
                    container.innerHTML = updates.map(update => `
                        <div class="update-item">
                            <strong>${update.product_id}</strong> - ${update.update_type}: ${update.new_value}
                            <div class="update-time">${new Date(update.updated_at).toLocaleString()}</div>
                        </div>
                    `).join('');
                }
            } catch (error) {
                console.error('Failed to load recent updates:', error);
            }
        }

        // File handling for CSV import
        function handleFileSelect(event) {
            const file = event.target.files[0];
            if (file) {
                uploadFile(file);
            }
        }

        function handleDragOver(event) {
            event.preventDefault();
            event.stopPropagation();
            document.getElementById('upload-area').classList.add('dragover');
        }

        function handleDragLeave(event) {
            event.preventDefault();
            event.stopPropagation();
            document.getElementById('upload-area').classList.remove('dragover');
        }

        function handleDrop(event) {
            event.preventDefault();
            event.stopPropagation();
            document.getElementById('upload-area').classList.remove('dragover');
            
            const file = event.dataTransfer.files[0];
            if (file && file.name.endsWith('.csv')) {
                uploadFile(file);
            } else {
                showImportMessage('error', 'Please upload a CSV file');
            }
        }

        async function uploadFile(file) {
            const formData = new FormData();
            formData.append('file', file);
            
            const resultDiv = document.getElementById('import-result');
            resultDiv.innerHTML = '<div class="alert alert-info">Importing... <span class="loading"></span></div>';
            
            try {
                const response = await fetch('/api/import-csv', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    resultDiv.innerHTML = `
                        <div class="alert alert-success">
                            ✅ Successfully imported ${result.imported} items!
                        </div>
                    `;
                    updateStats();
                    loadFrequentItems();
                } else {
                    resultDiv.innerHTML = `
                        <div class="alert alert-error">
                            ❌ Import failed: ${result.error}
                        </div>
                    `;
                }
            } catch (error) {
                resultDiv.innerHTML = `
                    <div class="alert alert-error">
                        ❌ Import failed: ${error.message}
                    </div>
                `;
            }
        }

        // Export database
        async function exportDatabase() {
            try {
                const response = await fetch('/api/export-database');
                const blob = await response.blob();
                
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `greenfield_inventory_${new Date().toISOString().split('T')[0]}.csv`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } catch (error) {
                console.error('Export failed:', error);
            }
        }

        // Load export statistics
        async function loadExportStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                document.getElementById('export-stats').innerHTML = `
                    <div style="display: grid; gap: 1rem;">
                        <div>📦 Total Items in Database: <strong>${stats.items_discovered.toLocaleString()}</strong></div>
                        <div>✅ Verified Items: <strong>${stats.items_cached.toLocaleString()}</strong></div>
                        <div>📅 Last Import: <strong>${stats.last_import ? new Date(stats.last_import).toLocaleString() : 'Never'}</strong></div>
                    </div>
                `;
            } catch (error) {
                console.error('Failed to load export stats:', error);
            }
        }

        // Load analytics
        async function loadAnalytics() {
            try {
                const response = await fetch('/api/analytics');
                const analytics = await response.json();
                
                document.getElementById('analytics-content').innerHTML = `
                    <div style="display: grid; gap: 2rem;">
                        <div>
                            <h3>📊 System Performance</h3>
                            <div style="display: grid; gap: 1rem; margin-top: 1rem;">
                                <div>🎯 Cache Hit Rate: <strong>${analytics.cache_hit_rate}%</strong></div>
                                <div>🔄 Total API Calls: <strong>${analytics.total_api_calls.toLocaleString()}</strong></div>
                                <div>⏱️ Uptime: <strong>${analytics.uptime}</strong></div>
                            </div>
                        </div>
                        
                        <div>
                            <h3>🔍 Search Patterns</h3>
                            <div style="margin-top: 1rem;">
                                ${analytics.top_searches.map(search => `
                                    <div style="padding: 0.5rem; background: #f8f9fa; margin-bottom: 0.5rem; border-radius: 4px;">
                                        "${search.pattern}" - ${search.frequency} searches
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                `;
            } catch (error) {
                console.error('Failed to load analytics:', error);
            }
        }
    </script>
</body>
</html>
    '''

# Routes
@app.get("/", response_class=HTMLResponse)
async def main_page():
    return get_main_interface()

@app.get("/api/search")
async def search_products(q: str):
    """Smart search endpoint"""
    results = await inventory_manager.smart_search(q)
    return results

@app.post("/api/validate-product")
async def validate_product(request: Request):
    """Validate and add new product"""
    data = await request.json()
    product_id = data.get('product_id', '').upper().strip()
    
    if not product_id:
        return {"success": False, "error": "Product ID required"}
    
    success, result = await inventory_manager.validate_and_add_item(product_id)
    
    return {
        "success": success,
        "product_id": product_id,
        **result
    }

@app.post("/api/update-inventory")
async def update_inventory(request: Request):
    """Update inventory item"""
    data = await request.json()
    product_id = data.get('product_id')
    updates = data.get('updates', {})
    
    if not product_id:
        return {"success": False, "error": "Product ID required"}
    
    success, result = await inventory_manager.update_item(product_id, updates)
    
    return {
        "success": success,
        **result
    }

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    return {
        **system_state,
        "uptime": str(datetime.now() - system_state["startup_time"])
    }

@app.get("/api/frequent-items")
async def get_frequent_items():
    """Get frequently used items"""
    return await inventory_manager.get_frequent_items()

@app.get("/api/recent-updates")
async def get_recent_updates():
    """Get recent update history"""
    return await inventory_manager.get_recent_updates()

@app.post("/api/import-csv")
async def import_csv(file: UploadFile = File(...)):
    """Import CSV file"""
    contents = await file.read()
    result = await inventory_manager.import_csv(contents)
    return result

@app.get("/api/export-database")
async def export_database():
    """Export database to CSV"""
    csv_data = await inventory_manager.export_database()
    
    return StreamingResponse(
        io.BytesIO(csv_data),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=greenfield_inventory_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )

@app.get("/api/analytics")
async def get_analytics():
    """Get system analytics"""
    # Calculate cache hit rate
    total_cache_ops = system_state["cache_hits"] + system_state["cache_misses"]
    cache_hit_rate = 0 if total_cache_ops == 0 else round((system_state["cache_hits"] / total_cache_ops) * 100, 1)
    
    # Get top search patterns
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT pattern, frequency 
            FROM search_patterns 
            ORDER BY frequency DESC 
            LIMIT 10
        ''')
        top_searches = [
            {"pattern": row[0], "frequency": row[1]}
            for row in await cursor.fetchall()
        ]
    
    return {
        "cache_hit_rate": cache_hit_rate,
        "total_api_calls": system_state["api_calls"],
        "uptime": str(datetime.now() - system_state["startup_time"]),
        "top_searches": top_searches
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")