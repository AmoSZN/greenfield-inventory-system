#!/usr/bin/env python3
"""
Greenfield Metal Sales - Production Inventory System v2.4
24/7 Cloud-hosted inventory management with real-time Paradigm integration
"""

import asyncio
import aiosqlite
import httpx
import logging
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paradigm API Configuration
PARADIGM_BASE_URL = "https://greenfieldapi.para-apps.com"
PARADIGM_API_KEY = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
PARADIGM_USERNAME = "web_admin"
PARADIGM_PASSWORD = "ChangeMe#123!"

# Database path
DB_PATH = "data/smart_inventory.db"

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

class ProductionInventoryManager:
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
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/user/Auth/GetToken",
                    json=auth_data,
                    headers={"X-API-Key": self.api_key}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.auth_token = data.get("token") or data.get("access_token")
                    logger.info("✅ Paradigm authentication successful")
                    return True
                else:
                    logger.error(f"❌ Authentication failed: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    async def get_inventory_items(self, skip: int = 0, take: int = 10000):
        """Get inventory items from Paradigm - now retrieves ALL items"""
        if not self.auth_token:
            if not await self.authenticate():
                return {"error": "Authentication failed"}
        
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.auth_token}",
                    "X-API-Key": self.api_key
                }
                
                # Use a very large take value to get ALL items
                response = await client.get(
                    f"{self.base_url}/api/Items/GetItems/{skip}/{take}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    items = response.json()
                    logger.info(f"✅ Retrieved {len(items)} items from Paradigm (ALL products)")
                    return {"success": True, "items": items, "count": len(items)}
                else:
                    logger.error(f"❌ GetItems failed: {response.status_code} - {response.text}")
                    return {"error": f"API call failed: {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"❌ GetItems error: {e}")
            return {"error": str(e)}
    
    async def update_item_quantity(self, product_id: str, new_quantity: int):
        """Update item quantity in Paradigm"""
        if not self.auth_token:
            if not await self.authenticate():
                return {"error": "Authentication failed"}
        
        try:
            # Get ALL items from Paradigm to find the one to update
            items_response = await self.get_inventory_items(0, 10000)
            if "error" in items_response:
                return items_response
            
            # Find the item to update among ALL items
            current_item = None
            for item in items_response.get("items", []):
                if item.get("strProductID") == product_id:
                    current_item = item.copy()
                    break
            
            if not current_item:
                return {"error": f"Item {product_id} not found in Paradigm inventory"}
            
            # Update the quantity using the correct Paradigm field name
            current_item["decUnitsInStock"] = new_quantity
            
            async with httpx.AsyncClient() as client:
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
                    logger.info(f"✅ Updated {product_id} to quantity {new_quantity}")
                    return {"success": True, "product_id": product_id, "new_quantity": new_quantity}
                else:
                    logger.error(f"❌ UpdateItem failed: {response.status_code} - {response.text}")
                    return {"error": f"Update failed: {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"❌ UpdateItem error: {e}")
            return {"error": str(e)}
    
    async def sync_to_local_database(self):
        """Sync Paradigm data to local database"""
        try:
            # Get items from Paradigm
            response = await self.get_inventory_items(0, 10000) # Use a large take for sync
            if "error" in response:
                return response
            
            items = response.get("items", [])
            
            # Update local database
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
                    product_id = item.get("strProductID")
                    description = item.get("memDescription")
                    quantity = item.get("decUnitsInStock") or 0
                    
                    if product_id:
                        await db.execute('''
                            INSERT OR REPLACE INTO inventory 
                            (product_id, description, current_quantity, last_updated)
                            VALUES (?, ?, ?, ?)
                        ''', (product_id, description, quantity, datetime.now()))
                
                await db.commit()
            
            logger.info(f"✅ Synced {len(items)} items to local database")
            return {"success": True, "items_synced": len(items)}
            
        except Exception as e:
            logger.error(f"❌ Sync error: {e}")
            return {"error": str(e)}

# Initialize inventory manager
inventory_manager = ProductionInventoryManager()

# Create FastAPI app
app = FastAPI(title="Greenfield Metal Sales Inventory System", version="2.4")

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
    """Initialize system on startup"""
    logger.info("🚀 Starting Greenfield Metal Sales Inventory System v2.4")
    
    # Initialize database
    try:
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
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
    
    # Test Paradigm connection
    auth_result = await inventory_manager.authenticate()
    if auth_result:
        logger.info("✅ Paradigm API connection successful")
    else:
        logger.error("❌ Paradigm API connection failed")

@app.get("/", response_class=HTMLResponse)
async def main_page():
    """Main dashboard page - State of the Art Design"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Greenfield Metal Sales - AI-Powered Inventory Management</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
                min-height: 100vh;
                line-height: 1.6;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .header {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.8em;
                font-weight: 700;
                background: linear-gradient(135deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 10px;
            }
            
            .header p {
                font-size: 1.2em;
                color: #666;
                margin-bottom: 5px;
            }
            
            .version-badge {
                display: inline-block;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 8px 16px;
                border-radius: 25px;
                font-size: 0.9em;
                font-weight: bold;
                margin-left: 15px;
            }
            
            .main-content {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                margin-bottom: 30px;
            }
            
            .search-section {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            
            .search-section h2 {
                font-size: 1.8em;
                margin-bottom: 20px;
                color: #2c3e50;
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
                padding: 15px 20px;
                padding-left: 50px;
                border: 2px solid #e1e8ed;
                border-radius: 15px;
                font-size: 16px;
                transition: all 0.3s ease;
                background: white;
            }
            
            .search-input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            .search-icon {
                position: absolute;
                left: 15px;
                top: 50%;
                transform: translateY(-50%);
                color: #667eea;
                font-size: 18px;
            }
            
            .search-button {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 15px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                width: 100%;
            }
            
            .search-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }
            
            .results-section {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                max-height: 600px;
                overflow-y: auto;
            }
            
            .results-section h2 {
                font-size: 1.8em;
                margin-bottom: 20px;
                color: #2c3e50;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .results-container {
                display: none;
            }
            
            .results-container.active {
                display: block;
            }
            
            .result-item {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 15px;
                border-left: 4px solid #667eea;
                transition: all 0.3s ease;
            }
            
            .result-item:hover {
                transform: translateX(5px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            
            .result-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            
            .product-id {
                font-size: 1.2em;
                font-weight: 700;
                color: #2c3e50;
            }
            
            .quantity-badge {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 0.9em;
                font-weight: 600;
            }
            
            .product-description {
                color: #666;
                margin-bottom: 10px;
                font-size: 1.1em;
            }
            
            .product-details {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                font-size: 0.9em;
                color: #888;
            }
            
            .detail-item {
                display: flex;
                align-items: center;
                gap: 5px;
            }
            
            .loading {
                text-align: center;
                padding: 40px;
                color: #667eea;
                font-size: 1.2em;
            }
            
            .no-results {
                text-align: center;
                padding: 40px;
                color: #666;
                font-size: 1.1em;
            }
            
            .stats-section {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
            }
            
            .stat-card {
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                border-radius: 15px;
                padding: 25px;
                text-align: center;
                border-left: 4px solid #667eea;
            }
            
            .stat-icon {
                font-size: 2em;
                color: #667eea;
                margin-bottom: 15px;
            }
            
            .stat-number {
                font-size: 2em;
                font-weight: 700;
                color: #2c3e50;
                margin-bottom: 5px;
            }
            
            .stat-label {
                color: #666;
                font-size: 1em;
            }
            
            .actions-section {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            
            .actions-section h2 {
                font-size: 1.8em;
                margin-bottom: 20px;
                color: #2c3e50;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .action-buttons {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
            }
            
            .action-button {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 15px 20px;
                border-radius: 15px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            }
            
            .action-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }
            
            .action-button.secondary {
                background: linear-gradient(135deg, #6c757d, #495057);
            }
            
            .action-button.success {
                background: linear-gradient(135deg, #28a745, #20c997);
            }
            
            .action-button.warning {
                background: linear-gradient(135deg, #ffc107, #fd7e14);
            }
            
            .footer {
                text-align: center;
                padding: 30px;
                color: white;
                font-size: 0.9em;
            }
            
            @media (max-width: 768px) {
                .main-content {
                    grid-template-columns: 1fr;
                }
                
                .header h1 {
                    font-size: 2.2em;
                }
                
                .stats-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1><i class="fas fa-industry"></i> Greenfield Metal Sales</h1>
                <p>AI-Powered Inventory Management System <span class="version-badge">v2.5</span></p>
                <p>24/7 Cloud-Hosted with Real-Time Paradigm ERP Integration</p>
            </div>
            
            <div class="stats-section">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon"><i class="fas fa-database"></i></div>
                        <div class="stat-number" id="totalItems">-</div>
                        <div class="stat-label">Total Products</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon"><i class="fas fa-sync-alt"></i></div>
                        <div class="stat-number" id="lastSync">-</div>
                        <div class="stat-label">Last Sync</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon"><i class="fas fa-link"></i></div>
                        <div class="stat-number" id="paradigmStatus">-</div>
                        <div class="stat-label">Paradigm Status</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon"><i class="fas fa-server"></i></div>
                        <div class="stat-number" id="systemStatus">-</div>
                        <div class="stat-label">System Status</div>
                    </div>
                </div>
            </div>
            
            <div class="main-content">
                <div class="search-section">
                    <h2><i class="fas fa-search"></i> Search Inventory</h2>
                    <div class="search-container">
                        <i class="fas fa-search search-icon"></i>
                        <input type="text" class="search-input" id="searchInput" placeholder="Search by product ID, description, or category...">
                    </div>
                    <button class="search-button" onclick="searchProducts()">
                        <i class="fas fa-search"></i> Search Products
                    </button>
                </div>
                
                <div class="results-section">
                    <h2><i class="fas fa-list"></i> Search Results</h2>
                    <div class="results-container" id="resultsContainer">
                        <div class="no-results">
                            <i class="fas fa-search" style="font-size: 3em; color: #ddd; margin-bottom: 20px;"></i>
                            <p>Enter a search term to find products</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="actions-section">
                <h2><i class="fas fa-cogs"></i> System Actions</h2>
                <div class="action-buttons">
                    <button class="action-button" onclick="testAuth()">
                        <i class="fas fa-key"></i> Test Authentication
                    </button>
                    <button class="action-button secondary" onclick="getAllItems()">
                        <i class="fas fa-download"></i> Get All Items
                    </button>
                    <button class="action-button success" onclick="syncDatabase()">
                        <i class="fas fa-sync"></i> Sync Database
                    </button>
                    <button class="action-button warning" onclick="updateTestItem()">
                        <i class="fas fa-edit"></i> Test Update
                    </button>
                </div>
            </div>
            
            <div class="footer">
                <p>© 2024 Greenfield Metal Sales - AI-Powered Inventory Management System</p>
                <p>Production Environment | Version 2.5 | Render.com Deployment</p>
            </div>
        </div>
        
        <script>
            // Load stats on page load
            document.addEventListener('DOMContentLoaded', function() {
                loadStats();
            });
            
            async function loadStats() {
                try {
                    const response = await fetch('/api/stats');
                    const data = await response.json();
                    
                    if (data.total_items !== undefined) {
                        document.getElementById('totalItems').textContent = data.total_items.toLocaleString();
                    }
                    
                    if (data.last_sync) {
                        document.getElementById('lastSync').textContent = 'Active';
                    } else {
                        document.getElementById('lastSync').textContent = 'Never';
                    }
                    
                    document.getElementById('paradigmStatus').textContent = data.paradigm_connected ? 'Connected' : 'Disconnected';
                    document.getElementById('systemStatus').textContent = 'Online';
                    
                } catch (error) {
                    console.error('Error loading stats:', error);
                }
            }
            
            async function searchProducts() {
                const searchTerm = document.getElementById('searchInput').value.trim();
                if (!searchTerm) {
                    alert('Please enter a search term');
                    return;
                }
                
                const resultsContainer = document.getElementById('resultsContainer');
                resultsContainer.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Searching...</div>';
                resultsContainer.classList.add('active');
                
                try {
                    const response = await fetch(`/api/paradigm/search?q=${encodeURIComponent(searchTerm)}`);
                    const data = await response.json();
                    
                    if (data.success && data.items && data.items.length > 0) {
                        displayResults(data.items);
                    } else {
                        resultsContainer.innerHTML = `
                            <div class="no-results">
                                <i class="fas fa-search" style="font-size: 3em; color: #ddd; margin-bottom: 20px;"></i>
                                <p>No products found for "${searchTerm}"</p>
                                <p style="font-size: 0.9em; color: #999;">Try a different search term</p>
                            </div>
                        `;
                    }
                } catch (error) {
                    resultsContainer.innerHTML = `
                        <div class="no-results">
                            <i class="fas fa-exclamation-triangle" style="font-size: 3em; color: #ffc107; margin-bottom: 20px;"></i>
                            <p>Error searching products</p>
                            <p style="font-size: 0.9em; color: #999;">${error.message}</p>
                        </div>
                    `;
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
                                <i class="fas fa-ruler"></i>
                                <span>Unit: ${item.unit_measure || 'N/A'}</span>
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
            
            // Handle Enter key in search input
            document.getElementById('searchInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchProducts();
                }
            });
            
            async function testAuth() {
                try {
                    const response = await fetch('/api/paradigm/auth');
                    const data = await response.json();
                    alert(data.success ? '✅ Authentication successful!' : '❌ Authentication failed');
                } catch (error) {
                    alert('❌ Error testing authentication');
                }
            }
            
            async function getAllItems() {
                try {
                    const response = await fetch('/api/paradigm/items?skip=0&take=10000');
                    const data = await response.json();
                    alert(`✅ Retrieved ${data.count} items from Paradigm`);
                } catch (error) {
                    alert('❌ Error getting items');
                }
            }
            
            async function syncDatabase() {
                try {
                    const response = await fetch('/api/paradigm/sync', {method: 'POST'});
                    const data = await response.json();
                    alert(`✅ Synced ${data.items_synced} items to database`);
                    loadStats(); // Refresh stats
                } catch (error) {
                    alert('❌ Error syncing database');
                }
            }
            
            async function updateTestItem() {
                try {
                    const response = await fetch('/api/paradigm/update-quantity', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({product_id: 'RET4GAVLF', quantity: 999})
                    });
                    const data = await response.json();
                    alert(data.success ? '✅ Test update successful!' : '❌ Test update failed');
                } catch (error) {
                    alert('❌ Error testing update');
                }
            }
        </script>
    </body>
    </html>
    """)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.5",
        "timestamp": datetime.now().isoformat(),
        "service": "Greenfield Metal Sales Inventory System",
        "environment": "production",
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
            last_updated = last_update[0] if last_update and last_update[0] else "Never"
        
        return {
            "total_items": item_count,
            "last_sync": last_updated,
            "paradigm_connected": inventory_manager.auth_token is not None,
            "version": "2.4"
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {"error": str(e)}

@app.get("/api/paradigm/auth")
async def test_paradigm_auth():
    """Test Paradigm authentication"""
    result = await inventory_manager.authenticate()
    return {"success": result, "authenticated": inventory_manager.auth_token is not None}

@app.get("/api/paradigm/items")
async def get_paradigm_items(skip: int = 0, take: int = 100):
    """Get items from Paradigm"""
    return await inventory_manager.get_inventory_items(skip, take)

@app.post("/api/paradigm/update-quantity")
async def update_paradigm_quantity(request: Request):
    """Update item quantity in Paradigm"""
    try:
        data = await request.json()
        product_id = data.get("product_id")
        quantity = data.get("quantity")
        
        if not product_id or quantity is None:
            raise HTTPException(status_code=400, detail="product_id and quantity required")
        
        return await inventory_manager.update_item_quantity(product_id, quantity)
    except Exception as e:
        logger.error(f"Update quantity error: {e}")
        return {"error": str(e)}

@app.post("/api/paradigm/sync")
async def sync_paradigm_data():
    """Sync Paradigm data to local database"""
    return await inventory_manager.sync_to_local_database()

@app.get("/api/search")
async def search_inventory(q: str):
    """Search local inventory"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(
                "SELECT * FROM inventory WHERE product_id LIKE ? OR description LIKE ?",
                (f"%{q}%", f"%{q}%")
            )
            rows = await cursor.fetchall()
            
            items = []
            for row in rows:
                items.append({
                    "product_id": row[0],
                    "description": row[1],
                    "quantity": row[2],
                    "last_updated": row[3]
                })
            
            return {"success": True, "items": items, "count": len(items)}
    except Exception as e:
        logger.error(f"Search error: {e}")
        return {"error": str(e)}

@app.get("/api/paradigm/search")
async def search_paradigm_items(q: str):
    """Search for items in Paradigm by partial name or ID"""
    try:
        # Get ALL items from Paradigm
        response = await inventory_manager.get_inventory_items(0, 10000)
        if "error" in response:
            return response
        
        items = response.get("items", [])
        
        # Search through items
        search_term = q.lower()
        matching_items = []
        
        for item in items:
            product_id = (item.get("strProductID") or "").lower()
            description = (item.get("memDescription") or "").lower()
            
            if search_term in product_id or search_term in description:
                matching_items.append({
                    "product_id": item.get("strProductID"),
                    "description": item.get("memDescription"),
                    "current_quantity": item.get("decUnitsInStock", 0),
                    "unit_measure": item.get("strUnitMeasure"),
                    "category": item.get("strCategory")
                })
        
        return {
            "success": True, 
            "search_term": q,
            "items": matching_items, 
            "count": len(matching_items)
        }
        
    except Exception as e:
        logger.error(f"Paradigm search error: {e}")
        return {"error": str(e)}

@app.get("/test-webhook")
async def test_webhook():
    """Test webhook endpoint"""
    return {
        "status": "webhook_ready",
        "message": "Webhook endpoint is operational",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

