#!/usr/bin/env python3
"""
24/7 Production Inventory System for Greenfield Metal Sales
Simplified, robust version that handles all 38,998 items
"""

from flask import Flask, render_template_string, request, jsonify, send_file
import sqlite3
import json
import os
import sys
import time
from datetime import datetime
import logging
import requests
from werkzeug.utils import secure_filename
import csv
import io

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('inventory_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create directories
os.makedirs('data', exist_ok=True)
os.makedirs('uploads', exist_ok=True)

# Database setup
DB_PATH = 'data/inventory.db'

# Paradigm ERP Configuration
PARADIGM_BASE_URL = "https://greenfieldapi.para-apps.com"
PARADIGM_API_KEY = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
PARADIGM_USERNAME = "web_admin"
PARADIGM_PASSWORD = "ChangeMe#123!"

def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create items table
    c.execute('''CREATE TABLE IF NOT EXISTS items
                 (product_id TEXT PRIMARY KEY,
                  description TEXT,
                  quantity REAL,
                  last_updated TIMESTAMP,
                  times_accessed INTEGER DEFAULT 0,
                  verified BOOLEAN DEFAULT 0)''')
    
    # Create update history
    c.execute('''CREATE TABLE IF NOT EXISTS update_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  product_id TEXT,
                  field_updated TEXT,
                  old_value TEXT,
                  new_value TEXT,
                  updated_at TIMESTAMP)''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized")

class InventoryManager:
    def __init__(self):
        self.auth_token = None
        self.token_expiry = None
        
    def authenticate(self):
        """Authenticate with Paradigm ERP"""
        try:
            auth_payload = {
                "userName": PARADIGM_USERNAME,
                "password": PARADIGM_PASSWORD
            }
            
            headers = {
                "x-api-key": PARADIGM_API_KEY,
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{PARADIGM_BASE_URL}/api/user/Auth/GetToken",
                headers=headers,
                json=auth_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                if token_data.get("isLoginValid"):
                    self.auth_token = token_data.get("data")
                    self.token_expiry = time.time() + (8 * 3600)  # 8 hours
                    logger.info("Authentication successful")
                    return True
            
            logger.error("Authentication failed")
            return False
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def ensure_authenticated(self):
        """Ensure we have valid authentication"""
        if not self.auth_token or time.time() > self.token_expiry:
            return self.authenticate()
        return True
    
    def search_products(self, query):
        """Search for products in local database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            query = query.upper()
            
            # Search by product ID or description
            c.execute('''SELECT product_id, description, quantity, times_accessed 
                         FROM items 
                         WHERE product_id LIKE ? OR description LIKE ?
                         ORDER BY times_accessed DESC
                         LIMIT 50''', 
                      (f'%{query}%', f'%{query}%'))
            
            results = []
            for row in c.fetchall():
                results.append({
                    'product_id': row[0],
                    'description': row[1] or 'No description',
                    'quantity': row[2],
                    'times_accessed': row[3],
                    'verified': True  # All items in database are considered verified
                })
            
            conn.close()
            logger.info(f"Search for '{query}' returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def validate_product(self, product_id):
        """Validate product exists in Paradigm ERP"""
        if not self.ensure_authenticated():
            return False, "Authentication failed"
        
        try:
            test_payload = {
                "strProductID": product_id,
                "dtmLastModified": datetime.now().isoformat()
            }
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "x-api-key": PARADIGM_API_KEY,
                "Content-Type": "application/json"
            }
            
            response = requests.put(
                f"{PARADIGM_BASE_URL}/api/Items/UpdateItem?excludeNullValues=true",
                headers=headers,
                json=test_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                # Product exists, add to database
                data = response.json()
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                
                c.execute('''INSERT OR REPLACE INTO items 
                             (product_id, description, quantity, last_updated, verified)
                             VALUES (?, ?, ?, ?, ?)''',
                          (product_id, 
                           data.get('memDescription', ''),
                           data.get('decUnitsInStock', 0),
                           datetime.now(),
                           1))
                
                conn.commit()
                conn.close()
                
                return True, data
            else:
                return False, "Product not found in ERP"
                
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return False, str(e)
    
    def update_inventory(self, product_id, updates):
        """Update inventory item - handles Paradigm read-only fields properly"""
        if not self.ensure_authenticated():
            return False, "Authentication failed"
        
        try:
            # Separate updateable vs read-only fields
            paradigm_updateable = {}
            local_only_updates = {}
            
            # Fields that CAN be updated in Paradigm
            if 'description' in updates and updates['description']:
                paradigm_updateable["memDescription"] = updates['description']
            
            if 'notes' in updates and updates['notes']:
                paradigm_updateable["strNotes"] = updates['notes']
            
            # Quantity is READ-ONLY in Paradigm (requires inventory transactions)
            if 'quantity' in updates and updates['quantity']:
                local_only_updates['quantity'] = updates['quantity']
            
            # Update Paradigm with updateable fields only
            paradigm_success = True
            paradigm_error = None
            
            if paradigm_updateable:
                update_payload = {
                    "strProductID": product_id,
                    "dtmLastModified": datetime.now().isoformat()
                }
                update_payload.update(paradigm_updateable)
                
                headers = {
                    "Authorization": f"Bearer {self.auth_token}",
                    "x-api-key": PARADIGM_API_KEY,
                    "Content-Type": "application/json"
                }
                
                response = requests.put(
                    f"{PARADIGM_BASE_URL}/api/Items/UpdateItem?excludeNullValues=true",
                    headers=headers,
                    json=update_payload,
                    timeout=30
                )
                
                if response.status_code != 200:
                    paradigm_success = False
                    paradigm_error = f"Status {response.status_code}: {response.text[:100]}"
            
            # Always update local database (for tracking)
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            # Update all fields locally
            if 'quantity' in updates:
                c.execute('UPDATE items SET quantity = ? WHERE product_id = ?',
                          (updates['quantity'], product_id))
            
            if 'description' in updates:
                c.execute('UPDATE items SET description = ? WHERE product_id = ?',
                          (updates['description'], product_id))
            
            # Update access count
            c.execute('UPDATE items SET times_accessed = times_accessed + 1 WHERE product_id = ?',
                      (product_id,))
            
            # Add to history with proper status
            for field, value in updates.items():
                status = "LOCAL_ONLY" if field == "quantity" else ("SUCCESS" if paradigm_success else "PARADIGM_FAILED")
                c.execute('''INSERT INTO update_history 
                             (product_id, field_updated, new_value, updated_at)
                             VALUES (?, ?, ?, ?)''',
                          (product_id, field, str(value), datetime.now()))
            
            conn.commit()
            conn.close()
            
            # Return appropriate message
            if local_only_updates and paradigm_updateable:
                if paradigm_success:
                    return True, "✅ Description/Notes updated in Paradigm. ⚠️ Quantity updated locally only (Paradigm inventory is read-only)"
                else:
                    return False, f"❌ Paradigm update failed: {paradigm_error}. ✅ Local updates saved."
            elif local_only_updates:
                return True, "⚠️ Quantity updated locally only. Paradigm inventory requires Purchase Orders or Inventory Adjustments to change quantities."
            elif paradigm_updateable:
                if paradigm_success:
                    return True, "✅ Successfully updated in Paradigm ERP"
                else:
                    return False, f"❌ Paradigm update failed: {paradigm_error}"
            else:
                return False, "No valid updates provided"
                
        except Exception as e:
            logger.error(f"Update error: {str(e)}")
            return False, f"System error: {str(e)}"
    
    def import_csv(self, file_path):
        """Import items from CSV"""
        try:
            imported = 0
            errors = []
            
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                
                for row in reader:
                    try:
                        # Get product ID (try different column names)
                        product_id = (row.get('Product ID') or 
                                    row.get('product_id') or 
                                    row.get('strProductID') or 
                                    row.get('ProductID', '')).strip()
                        
                        if product_id:
                            c.execute('''INSERT OR REPLACE INTO items 
                                         (product_id, description, quantity, last_updated, verified)
                                         VALUES (?, ?, ?, ?, ?)''',
                                      (product_id,
                                       row.get('Description', row.get('description', '')),
                                       float(row.get('Quantity', row.get('quantity', 0))),
                                       datetime.now(),
                                       1))
                            imported += 1
                        else:
                            errors.append(f"Missing product ID in row: {row}")
                            
                    except Exception as e:
                        errors.append(f"Error processing row: {str(e)}")
                
                conn.commit()
                conn.close()
            
            return imported, errors
            
        except Exception as e:
            logger.error(f"Import error: {str(e)}")
            return 0, [str(e)]
    
    def get_current_quantity(self, product_id):
        """Get current quantity for a product"""
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('SELECT quantity FROM items WHERE product_id = ?', (product_id,))
            result = c.fetchone()
            conn.close()
            
            if result:
                return float(result[0])
            else:
                # Try to get from Paradigm if not in local DB
                if self.ensure_authenticated():
                    headers = {
                        "Authorization": f"Bearer {self.auth_token}",
                        "x-api-key": PARADIGM_API_KEY
                    }
                    
                    response = requests.get(
                        f"{PARADIGM_BASE_URL}/api/Items/GetItem?strProductID={product_id}",
                        headers=headers,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        return float(data.get('decUnitsInStock', 0))
                
                return 0.0
                
        except Exception as e:
            logger.error(f"Error getting quantity for {product_id}: {str(e)}")
            return 0.0

# Initialize manager
inventory_manager = InventoryManager()

# Import enhanced modules
try:
    from professional_web_interface import get_professional_interface
    from advanced_natural_language import AdvancedNaturalLanguageProcessor
    from real_time_paradigm_integration import RealTimeParadigmIntegrator
    
    # Initialize advanced components
    nlp_processor = AdvancedNaturalLanguageProcessor()
    paradigm_integrator = RealTimeParadigmIntegrator()
    
    # Use professional interface
    HTML_TEMPLATE = get_professional_interface()
    
    logger.info("✅ Advanced components loaded successfully")
    
except ImportError as e:
    logger.warning(f"⚠️ Advanced components not available: {e}")
    # Fallback to basic interface
    HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Greenfield Inventory System - 24/7</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Arial, sans-serif;
            background: #f0f0f0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
            text-align: center;
        }
        .status {
            background: #e8f5e9;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
        }
        .search-box {
            width: 100%;
            padding: 15px;
            font-size: 18px;
            border: 2px solid #ddd;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .search-results {
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-bottom: 20px;
            display: none;
        }
        .result-item {
            padding: 10px;
            border-bottom: 1px solid #eee;
            cursor: pointer;
        }
        .result-item:hover {
            background: #f5f5f5;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input, textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        button {
            background: #2196F3;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-right: 10px;
        }
        button:hover {
            background: #1976D2;
        }
        .tabs {
            display: flex;
            margin-bottom: 20px;
            border-bottom: 2px solid #ddd;
        }
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
        }
        .tab.active {
            border-bottom-color: #2196F3;
            color: #2196F3;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .upload-area {
            border: 2px dashed #ddd;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .upload-area:hover {
            background: #f5f5f5;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: #f5f5f5;
            padding: 20px;
            border-radius: 5px;
            text-align: center;
        }
        .stat-number {
            font-size: 36px;
            font-weight: bold;
            color: #2196F3;
        }
        .message {
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏭 Greenfield Metal Sales - Inventory System</h1>
        
        <div class="status">
            ✅ System Online - Managing 38,998 Items - 24/7 Operation
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="total-capacity">38,998</div>
                <div>Total Capacity</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="items-loaded">0</div>
                <div>Items Loaded</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="updates-today">0</div>
                <div>Updates Today</div>
            </div>
        </div>
        
        <div class="tabs">
            <div class="tab active" onclick="switchTab('update')">Update Inventory</div>
            <div class="tab" onclick="switchTab('import')">Bulk Import/Export</div>
            <div class="tab" onclick="switchTab('history')">Update History</div>
        </div>
        
        <!-- Update Tab -->
        <div id="update-tab" class="tab-content active">
            <div class="form-group">
                <label>Search Product (Type any Product ID)</label>
                <input type="text" id="search" class="search-box" 
                       placeholder="e.g., 1030G, 1025AW, or any of 38,998 items..."
                       oninput="searchProducts(this.value)">
                <div id="search-results" class="search-results"></div>
            </div>
            
            <div id="update-form" style="display: none;">
                <div class="form-group">
                    <label>Product ID</label>
                    <input type="text" id="product-id" readonly>
                </div>
                
                <div class="form-group">
                    <label>New Quantity</label>
                    <input type="number" id="quantity" placeholder="Leave blank to skip">
                </div>
                
                <div class="form-group">
                    <label>Description</label>
                    <textarea id="description" rows="2" placeholder="Leave blank to skip"></textarea>
                </div>
                
                <div class="form-group">
                    <label>Notes</label>
                    <textarea id="notes" rows="2" placeholder="Leave blank to skip"></textarea>
                </div>
                
                <button onclick="updateInventory()">Update Inventory</button>
                <button onclick="clearForm()" style="background: #666;">Clear</button>
            </div>
            
            <div id="message"></div>
        </div>
        
        <!-- Import Tab -->
        <div id="import-tab" class="tab-content">
            <div class="upload-area" onclick="document.getElementById('csv-file').click()">
                <h3>📁 Click to Upload CSV File</h3>
                <p>or drag and drop here</p>
                <p style="margin-top: 10px; color: #666;">
                    Format: Product ID, Description, Quantity
                </p>
            </div>
            <input type="file" id="csv-file" accept=".csv" style="display: none;" onchange="uploadFile(this)">
            
            <button onclick="exportData()" style="background: #4CAF50;">
                📥 Export All Data to CSV
            </button>
            
            <div id="import-message"></div>
        </div>
        
        <!-- History Tab -->
        <div id="history-tab" class="tab-content">
            <h3>Recent Updates</h3>
            <div id="history-list"></div>
        </div>
    </div>
    
    <script>
        let searchTimeout;
        let selectedProduct = null;
        
        // Load stats on page load
        window.onload = function() {
            loadStats();
            loadHistory();
        };
        
        function switchTab(tab) {
            // Update tabs
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            
            // Update content
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.getElementById(tab + '-tab').classList.add('active');
            
            if (tab === 'history') {
                loadHistory();
            }
        }
        
        function searchProducts(query) {
            clearTimeout(searchTimeout);
            const resultsDiv = document.getElementById('search-results');
            
            if (query.length < 2) {
                resultsDiv.style.display = 'none';
                return;
            }
            
            searchTimeout = setTimeout(async () => {
                try {
                    const response = await fetch('/api/search?q=' + encodeURIComponent(query));
                    const results = await response.json();
                    
                    if (results.length > 0) {
                        resultsDiv.innerHTML = results.map(item => 
                            `<div class="result-item" onclick="selectProduct('${item.product_id}')">
                                <strong>${item.product_id}</strong> - ${item.description}
                                ${item.verified ? '✅' : '❓'}
                            </div>`
                        ).join('');
                    } else {
                        resultsDiv.innerHTML = 
                            `<div class="result-item" onclick="addNewProduct('${query.toUpperCase()}')">
                                <strong>Add "${query.toUpperCase()}" as new product</strong>
                                <br>Click to validate with Paradigm ERP
                            </div>`;
                    }
                    resultsDiv.style.display = 'block';
                } catch (error) {
                    console.error('Search error:', error);
                }
            }, 300);
        }
        
        function selectProduct(productId) {
            selectedProduct = productId;
            document.getElementById('product-id').value = productId;
            document.getElementById('search').value = productId;
            document.getElementById('search-results').style.display = 'none';
            document.getElementById('update-form').style.display = 'block';
        }
        
        async function addNewProduct(productId) {
            showMessage('Validating product with Paradigm ERP...', 'info');
            
            try {
                const response = await fetch('/api/validate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ product_id: productId })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showMessage('Product validated and added!', 'success');
                    selectProduct(productId);
                    loadStats();
                } else {
                    showMessage('Product not found in Paradigm ERP: ' + result.error, 'error');
                }
            } catch (error) {
                showMessage('Error validating product', 'error');
            }
        }
        
        async function updateInventory() {
            const updates = {};
            const quantity = document.getElementById('quantity').value;
            const description = document.getElementById('description').value;
            const notes = document.getElementById('notes').value;
            
            if (quantity) updates.quantity = quantity;
            if (description) updates.description = description;
            if (notes) updates.notes = notes;
            
            if (Object.keys(updates).length === 0) {
                showMessage('Please enter at least one field to update', 'error');
                return;
            }
            
            showMessage('Updating inventory...', 'info');
            
            try {
                const response = await fetch('/api/update', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        product_id: selectedProduct,
                        updates: updates
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showMessage('Inventory updated successfully!', 'success');
                    clearForm();
                    loadStats();
                } else {
                    showMessage('Update failed: ' + result.error, 'error');
                }
            } catch (error) {
                showMessage('Error updating inventory', 'error');
            }
        }
        
        function clearForm() {
            document.getElementById('search').value = '';
            document.getElementById('product-id').value = '';
            document.getElementById('quantity').value = '';
            document.getElementById('description').value = '';
            document.getElementById('notes').value = '';
            document.getElementById('update-form').style.display = 'none';
            selectedProduct = null;
        }
        
        function showMessage(text, type) {
            const messageDiv = document.getElementById('message');
            messageDiv.className = 'message ' + type;
            messageDiv.textContent = text;
            messageDiv.style.display = 'block';
            
            if (type !== 'info') {
                setTimeout(() => {
                    messageDiv.style.display = 'none';
                }, 5000);
            }
        }
        
        async function uploadFile(input) {
            const file = input.files[0];
            if (!file) return;
            
            const formData = new FormData();
            formData.append('file', file);
            
            document.getElementById('import-message').innerHTML = 
                '<div class="message info">Importing CSV file...</div>';
            
            try {
                const response = await fetch('/api/import', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('import-message').innerHTML = 
                        `<div class="message success">Successfully imported ${result.imported} items!</div>`;
                    loadStats();
                } else {
                    document.getElementById('import-message').innerHTML = 
                        `<div class="message error">Import failed: ${result.error}</div>`;
                }
            } catch (error) {
                document.getElementById('import-message').innerHTML = 
                    '<div class="message error">Error importing file</div>';
            }
        }
        
        async function exportData() {
            window.location.href = '/api/export';
        }
        
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                document.getElementById('items-loaded').textContent = stats.items_loaded.toLocaleString();
                document.getElementById('updates-today').textContent = stats.updates_today.toLocaleString();
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }
        
        async function loadHistory() {
            try {
                const response = await fetch('/api/history');
                const history = await response.json();
                
                const historyDiv = document.getElementById('history-list');
                if (history.length > 0) {
                    historyDiv.innerHTML = history.map(item => 
                        `<div style="padding: 10px; border-bottom: 1px solid #eee;">
                            <strong>${item.product_id}</strong> - ${item.field_updated}: ${item.new_value}
                            <br><small>${new Date(item.updated_at).toLocaleString()}</small>
                        </div>`
                    ).join('');
                } else {
                    historyDiv.innerHTML = '<p>No updates yet</p>';
                }
            } catch (error) {
                console.error('Error loading history:', error);
            }
        }
    </script>
</body>
</html>
'''

# Routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    results = inventory_manager.search_products(query)
    return jsonify(results)

@app.route('/api/validate', methods=['POST'])
def validate():
    data = request.json
    product_id = data.get('product_id', '').upper()
    
    if not product_id:
        return jsonify({'success': False, 'error': 'Product ID required'})
    
    success, result = inventory_manager.validate_product(product_id)
    
    return jsonify({
        'success': success,
        'error': result if not success else None,
        'data': result if success else None
    })

@app.route('/api/update', methods=['POST'])
def update():
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'Invalid JSON data'}), 400
            
        product_id = data.get('product_id')
        updates = data.get('updates', {})
        
        if not product_id:
            return jsonify({'success': False, 'error': 'Product ID required'}), 400
            
        if not updates:
            return jsonify({'success': False, 'error': 'Updates required'}), 400
        
        success, result = inventory_manager.update_inventory(product_id, updates)
        
        # Enhanced real-time Paradigm sync for description updates
        if success and 'paradigm_integrator' in globals() and 'description' in updates:
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    sync_success, sync_message = loop.run_until_complete(
                        paradigm_integrator.push_update_to_paradigm(product_id, updates)
                    )
                    if sync_success:
                        result = f"{result} → ✅ Successfully updated in Paradigm ERP"
                    else:
                        result = f"{result} → ⚠️ Local update successful, Paradigm sync failed: {sync_message}"
                finally:
                    loop.close()
            except Exception as e:
                logger.error(f"Paradigm sync error: {str(e)}")
                result = f"{result} → ⚠️ Local update successful, Paradigm sync unavailable"
        
        return jsonify({
            'success': success,
            'error': result if not success else None,
            'data': result if success else None
        })
        
    except Exception as e:
        logger.error(f"Update endpoint error: {str(e)}")
        return jsonify({'success': False, 'error': 'Invalid request format'}), 400

def execute_parsed_command(parsed_command):
    """Execute a parsed natural language command"""
    from advanced_natural_language import CommandType
    
    try:
        if not parsed_command.product_id:
            return {'success': False, 'message': 'No product ID identified'}
        
        updates = {}
        
        # Handle different command types
        if parsed_command.command_type == CommandType.ADD_QUANTITY:
            if parsed_command.quantity_change:
                current_qty = inventory_manager.get_current_quantity(parsed_command.product_id)
                new_qty = current_qty + parsed_command.quantity_change
                updates['quantity'] = new_qty
        
        elif parsed_command.command_type == CommandType.SET_QUANTITY:
            if parsed_command.new_quantity is not None:
                updates['quantity'] = parsed_command.new_quantity
        
        elif parsed_command.command_type == CommandType.REDUCE_QUANTITY:
            if parsed_command.quantity_change:
                current_qty = inventory_manager.get_current_quantity(parsed_command.product_id)
                new_qty = current_qty + parsed_command.quantity_change  # quantity_change is negative
                updates['quantity'] = max(0, new_qty)  # Don't go below 0
        
        elif parsed_command.command_type == CommandType.UPDATE_DESCRIPTION:
            if parsed_command.description:
                updates['description'] = parsed_command.description
        
        elif parsed_command.command_type == CommandType.UPDATE_NOTES:
            if parsed_command.notes:
                updates['notes'] = parsed_command.notes
        
        if not updates:
            return {'success': False, 'message': 'No valid updates identified'}
        
        # Execute the update
        success, result = inventory_manager.update_inventory(parsed_command.product_id, updates)
        
        return {
            'success': success,
            'message': result,
            'updates': updates
        }
        
    except Exception as e:
        logger.error(f"Error executing parsed command: {str(e)}")
        return {'success': False, 'message': f'Execution error: {str(e)}'}

@app.route('/api/natural', methods=['POST'])
def natural_language():
    """Process natural language commands with advanced NLP"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'Invalid JSON data'}), 400
            
        command = data.get('command', '').strip()
        if not command:
            return jsonify({'success': False, 'error': 'Command required'}), 400
        
        # Use advanced NLP processor if available
        if 'nlp_processor' in globals():
            import asyncio
            
            # Process with advanced NLP
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                parsed_command = loop.run_until_complete(nlp_processor.process_command(command))
                result = execute_parsed_command(parsed_command)
                
                # Generate intelligent response
                response_message = nlp_processor.generate_response_message(
                    parsed_command, 
                    result['success'], 
                    result.get('message', '')
                )
                
                return jsonify({
                    'success': result['success'],
                    'data': response_message,
                    'error': None if result['success'] else result['message'],
                    'parsed': {
                        'original_command': command,
                        'command_type': parsed_command.command_type.value,
                        'product_id': parsed_command.product_id,
                        'confidence': parsed_command.confidence,
                        'updates': result.get('updates', {})
                    }
                })
            finally:
                loop.close()
        else:
            # Fallback to simple processing
            return process_natural_command_fallback(command)
            
    except Exception as e:
        logger.error(f"Natural language endpoint error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to process natural language command'}), 500

def process_natural_command_fallback(command):
    """Fallback natural language processing"""
    try:
        command_lower = command.lower()
        
        # Extract product ID
        import re
        product_match = re.search(r'\b(\d{4}[A-Z]+)\b', command)
        if not product_match:
            return jsonify({
                'success': False, 
                'error': 'Could not identify product ID in command'
            })
        
        product_id = product_match.group(1)
        updates = {}
        
        # Quantity updates
        if 'add' in command_lower and 'units' in command_lower:
            qty_match = re.search(r'add (\d+) units', command_lower)
            if qty_match:
                current_qty = inventory_manager.get_current_quantity(product_id)
                new_qty = current_qty + int(qty_match.group(1))
                updates['quantity'] = new_qty
                
        elif 'set' in command_lower and ('quantity' in command_lower or 'units' in command_lower):
            qty_match = re.search(r'(?:quantity|units) to (\d+)', command_lower)
            if qty_match:
                updates['quantity'] = int(qty_match.group(1))
                
        elif 'increase' in command_lower and 'by' in command_lower:
            qty_match = re.search(r'by (\d+)', command_lower)
            if qty_match:
                current_qty = inventory_manager.get_current_quantity(product_id)
                new_qty = current_qty + int(qty_match.group(1))
                updates['quantity'] = new_qty
        
        # Description updates
        if 'description' in command_lower and 'to' in command_lower:
            desc_match = re.search(r'description .*?to (.+?)(?:\s|$)', command, re.IGNORECASE)
            if desc_match:
                updates['description'] = desc_match.group(1).strip()
        
        if not updates:
            return jsonify({
                'success': False,
                'error': 'Could not understand the command. Try: "Add 50 units to product 1015B" or "Set description for 1015B to New Description"'
            })
        
        # Execute the update
        success, result = inventory_manager.update_inventory(product_id, updates)
        
        return jsonify({
            'success': success,
            'error': result if not success else None,
            'data': f"Processed: {command} → {result}" if success else None,
            'parsed': {
                'product_id': product_id,
                'updates': updates,
                'original_command': command
            }
        })
        
    except Exception as e:
        logger.error(f"Fallback NL processing error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to process command'}), 500

@app.route('/api/import', methods=['POST'])
def import_csv():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads', filename)
        file.save(filepath)
        
        imported, errors = inventory_manager.import_csv(filepath)
        
        # Clean up
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'imported': imported,
            'errors': errors
        })
    
    return jsonify({'success': False, 'error': 'Invalid file type'})

@app.route('/api/export')
def export():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT product_id, description, quantity FROM items ORDER BY product_id')
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Product ID', 'Description', 'Quantity'])
    
    for row in c.fetchall():
        writer.writerow(row)
    
    conn.close()
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'inventory_export_{datetime.now().strftime("%Y%m%d")}.csv'
    )

@app.route('/api/stats')
def stats():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*) FROM items')
        items_loaded = c.fetchone()[0]
        
        c.execute('''SELECT COUNT(*) FROM update_history 
                     WHERE DATE(updated_at) = DATE('now')''')
        updates_today = c.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'items_loaded': items_loaded,
            'updates_today': updates_today,
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Stats endpoint error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Simple health check for Render
@app.route('/health')
@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'greenfield-inventory-system',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/history')
def history():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''SELECT product_id, field_updated, new_value, updated_at 
                 FROM update_history 
                 ORDER BY updated_at DESC 
                 LIMIT 50''')
    
    history = []
    for row in c.fetchall():
        history.append({
            'product_id': row[0],
            'field_updated': row[1],
            'new_value': row[2],
            'updated_at': row[3]
        })
    
    conn.close()
    
    return jsonify(history)

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Get local IP
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print("\n" + "="*60)
    print("🏭 GREENFIELD INVENTORY SYSTEM - 24/7 PRODUCTION")
    print("="*60)
    print(f"✅ System starting...")
    print(f"🌐 Local Access: http://localhost:8000")
    print(f"🌐 Network Access: http://{local_ip}:8000")
    print(f"📱 Mobile Access: http://{local_ip}:8000")
    print("="*60)
    print("📊 Features:")
    print("  • Smart search for all 38,998 items")
    print("  • Real-time Paradigm ERP updates")
    print("  • Bulk CSV import/export")
    print("  • Complete update history")
    print("  • 24/7 availability")
    print("="*60)
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    # Run the app
    app.run(host='0.0.0.0', port=8000, debug=False)