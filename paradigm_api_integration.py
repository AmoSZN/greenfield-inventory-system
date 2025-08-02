#!/usr/bin/env python3
"""
Paradigm ERP API Integration for Real-time Inventory Sync
"""

from flask import Flask, request, jsonify
import sqlite3
import httpx
import asyncio
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Paradigm Configuration
PARADIGM_BASE_URL = "https://greenfieldapi.para-apps.com"
PARADIGM_API_KEY = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
PARADIGM_USERNAME = "web_admin"
PARADIGM_PASSWORD = "ChangeMe#123!"

# Database path
DB_PATH = 'Data/inventory.db'

class ParadigmSync:
    def __init__(self):
        self.auth_token = None
        self.token_expiry = None
    
    async def authenticate(self):
        """Authenticate with Paradigm ERP"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{PARADIGM_BASE_URL}/api/Authenticate",
                json={
                    "userName": PARADIGM_USERNAME,
                    "password": PARADIGM_PASSWORD
                },
                headers={"x-api-key": PARADIGM_API_KEY}
            )
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("data", {}).get("token")
                logger.info("✅ Paradigm authentication successful")
                return True
            logger.error(f"❌ Authentication failed: {response.status_code}")
            return False
    
    async def sync_inventory_changes(self, product_id, new_quantity):
        """Sync inventory changes to Paradigm"""
        if not self.auth_token:
            await self.authenticate()
        
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{PARADIGM_BASE_URL}/api/Items/UpdateItem?excludeNullValues=true",
                headers={
                    "Authorization": f"Bearer {self.auth_token}",
                    "x-api-key": PARADIGM_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "strProductID": product_id,
                    "decUnitsInStock": new_quantity
                }
            )
            return response.status_code == 200

paradigm_sync = ParadigmSync()

# Webhook endpoint for Paradigm
@app.route('/webhook/paradigm/inventory', methods=['POST'])
async def paradigm_inventory_webhook():
    """Receive inventory updates from Paradigm"""
    try:
        data = request.get_json()
        logger.info(f"📥 Received webhook: {json.dumps(data, indent=2)}")
        
        # Extract inventory changes
        event_type = data.get('eventType', '')
        product_id = data.get('productId', '')
        
        if event_type == 'INVENTORY_UPDATE':
            new_quantity = data.get('newQuantity', 0)
            old_quantity = data.get('oldQuantity', 0)
            
            # Update local database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE items 
                SET quantity = ?, last_updated = ?
                WHERE product_id = ?
            ''', (new_quantity, datetime.now(), product_id))
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Updated {product_id}: {old_quantity} → {new_quantity}")
            
            return jsonify({
                'status': 'success',
                'message': f'Updated {product_id} to {new_quantity}'
            })
        
        return jsonify({'status': 'received'})
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# API endpoint for manual sync
@app.route('/api/sync/product/<product_id>', methods=['POST'])
async def sync_single_product(product_id):
    """Manually sync a single product with Paradigm"""
    try:
        # Get current quantity from database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT quantity FROM items WHERE product_id = ?', (product_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return jsonify({'error': 'Product not found'}), 404
        
        current_quantity = result[0]
        
        # Sync to Paradigm
        success = await paradigm_sync.sync_inventory_changes(product_id, current_quantity)
        
        if success:
            return jsonify({
                'status': 'success',
                'product_id': product_id,
                'quantity': current_quantity
            })
        else:
            return jsonify({'error': 'Sync failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API endpoint for bulk sync
@app.route('/api/sync/all', methods=['POST'])
async def sync_all_products():
    """Sync all products with Paradigm"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT product_id, quantity FROM items WHERE verified = 1')
        products = cursor.fetchall()
        conn.close()
        
        synced = 0
        failed = 0
        
        for product_id, quantity in products:
            if await paradigm_sync.sync_inventory_changes(product_id, quantity):
                synced += 1
            else:
                failed += 1
            
            # Progress update every 100 products
            if (synced + failed) % 100 == 0:
                logger.info(f"Progress: {synced + failed}/{len(products)}")
        
        return jsonify({
            'total': len(products),
            'synced': synced,
            'failed': failed
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check for monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'Paradigm API Integration',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Paradigm API Integration Service")
    print("=" * 50)
    print("Endpoints:")
    print("  - Webhook: http://localhost:5005/webhook/paradigm/inventory")
    print("  - Sync Single: http://localhost:5005/api/sync/product/<id>")
    print("  - Sync All: http://localhost:5005/api/sync/all")
    print("  - Health: http://localhost:5005/health")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5005, debug=False)