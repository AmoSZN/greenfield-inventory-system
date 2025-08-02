#!/usr/bin/env python3
"""
Professional Web Interface Enhancement
"""

PROFESSIONAL_HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Greenfield Metal Sales - AI Inventory Management</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --accent-color: #e74c3c;
            --success-color: #27ae60;
            --warning-color: #f39c12;
            --bg-light: #ecf0f1;
            --text-dark: #2c3e50;
            --text-light: #7f8c8d;
            --border-color: #bdc3c7;
            --shadow: 0 2px 10px rgba(0,0,0,0.1);
            --shadow-hover: 0 4px 20px rgba(0,0,0,0.15);
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: var(--text-dark);
        }

        .header {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            box-shadow: var(--shadow);
            position: sticky;
            top: 0;
            z-index: 1000;
        }

        .header-content {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .logo i {
            font-size: 2rem;
            color: var(--secondary-color);
        }

        .logo h1 {
            color: var(--primary-color);
            font-size: 1.5rem;
            font-weight: 600;
        }

        .status-indicators {
            display: flex;
            gap: 1rem;
            align-items: center;
        }

        .status-badge {
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .status-online {
            background: rgba(39, 174, 96, 0.1);
            color: var(--success-color);
            border: 1px solid rgba(39, 174, 96, 0.3);
        }

        .status-syncing {
            background: rgba(52, 152, 219, 0.1);
            color: var(--secondary-color);
            border: 1px solid rgba(52, 152, 219, 0.3);
        }

        .main-container {
            max-width: 1400px;
            margin: 2rem auto;
            padding: 0 2rem;
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 2rem;
        }

        .sidebar {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: var(--shadow);
            height: fit-content;
            position: sticky;
            top: 100px;
        }

        .sidebar h3 {
            color: var(--primary-color);
            margin-bottom: 1rem;
            font-size: 1.1rem;
        }

        .quick-stats {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .stat-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem;
            background: var(--bg-light);
            border-radius: 8px;
            transition: transform 0.2s ease;
        }

        .stat-item:hover {
            transform: translateY(-2px);
        }

        .stat-value {
            font-weight: 600;
            color: var(--secondary-color);
        }

        .main-content {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 2rem;
            box-shadow: var(--shadow);
        }

        .search-section {
            margin-bottom: 2rem;
        }

        .search-container {
            position: relative;
            margin-bottom: 1rem;
        }

        .search-input {
            width: 100%;
            padding: 1rem 1rem 1rem 3rem;
            border: 2px solid var(--border-color);
            border-radius: 10px;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: white;
        }

        .search-input:focus {
            outline: none;
            border-color: var(--secondary-color);
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        }

        .search-icon {
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-light);
            font-size: 1.1rem;
        }

        .natural-language-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 2rem;
        }

        .nl-title {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1rem;
            font-size: 1.1rem;
            font-weight: 600;
        }

        .nl-input {
            width: 100%;
            padding: 1rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            margin-bottom: 1rem;
        }

        .nl-examples {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }

        .nl-example {
            background: rgba(255,255,255,0.2);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: background 0.2s ease;
        }

        .nl-example:hover {
            background: rgba(255,255,255,0.3);
        }

        .results-section {
            margin-top: 2rem;
        }

        .results-grid {
            display: grid;
            gap: 1rem;
        }

        .result-card {
            background: white;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .result-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-hover);
            border-color: var(--secondary-color);
        }

        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }

        .product-id {
            font-size: 1.2rem;
            font-weight: 600;
            color: var(--primary-color);
        }

        .quantity-badge {
            background: var(--success-color);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 15px;
            font-size: 0.85rem;
            font-weight: 500;
        }

        .result-description {
            color: var(--text-light);
            margin-bottom: 1rem;
            line-height: 1.5;
        }

        .result-actions {
            display: flex;
            gap: 0.5rem;
        }

        .btn {
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .btn-primary {
            background: var(--secondary-color);
            color: white;
        }

        .btn-primary:hover {
            background: #2980b9;
        }

        .btn-success {
            background: var(--success-color);
            color: white;
        }

        .btn-success:hover {
            background: #229954;
        }

        .btn-outline {
            background: transparent;
            border: 1px solid var(--border-color);
            color: var(--text-dark);
        }

        .btn-outline:hover {
            background: var(--bg-light);
        }

        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 2000;
        }

        .modal-content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: var(--shadow-hover);
            min-width: 400px;
            max-width: 90vw;
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }

        .modal-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: var(--primary-color);
        }

        .close-btn {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: var(--text-light);
        }

        .form-group {
            margin-bottom: 1rem;
        }

        .form-label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: var(--text-dark);
        }

        .form-input {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            font-size: 1rem;
        }

        .form-input:focus {
            outline: none;
            border-color: var(--secondary-color);
            box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.1);
        }

        .loading {
            display: none;
            text-align: center;
            padding: 2rem;
            color: var(--text-light);
        }

        .spinner {
            border: 3px solid var(--bg-light);
            border-top: 3px solid var(--secondary-color);
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .notification {
            position: fixed;
            top: 100px;
            right: 2rem;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 3000;
            transform: translateX(400px);
            transition: transform 0.3s ease;
        }

        .notification.show {
            transform: translateX(0);
        }

        .notification.success {
            background: var(--success-color);
        }

        .notification.error {
            background: var(--accent-color);
        }

        .notification.warning {
            background: var(--warning-color);
        }

        @media (max-width: 768px) {
            .main-container {
                grid-template-columns: 1fr;
                gap: 1rem;
                padding: 0 1rem;
            }
            
            .sidebar {
                position: static;
                order: 2;
            }
            
            .header-content {
                flex-direction: column;
                gap: 1rem;
            }
            
            .status-indicators {
                flex-wrap: wrap;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo">
                <i class="fas fa-industry"></i>
                <div>
                    <h1>Greenfield Metal Sales</h1>
                    <small>AI-Powered Inventory Management</small>
                </div>
            </div>
            <div class="status-indicators">
                <div class="status-badge status-online">
                    <i class="fas fa-circle"></i>
                    <span>System Online</span>
                </div>
                <div class="status-badge status-syncing">
                    <i class="fas fa-sync-alt"></i>
                    <span>Paradigm Sync</span>
                </div>
                <div class="status-badge">
                    <i class="fas fa-database"></i>
                    <span id="item-count">39,193 Items</span>
                </div>
            </div>
        </div>
    </header>

    <div class="main-container">
        <aside class="sidebar">
            <h3><i class="fas fa-chart-bar"></i> Quick Stats</h3>
            <div class="quick-stats">
                <div class="stat-item">
                    <span>Updates Today</span>
                    <span class="stat-value" id="updates-today">0</span>
                </div>
                <div class="stat-item">
                    <span>Last Sync</span>
                    <span class="stat-value" id="last-sync">Active</span>
                </div>
                <div class="stat-item">
                    <span>System Status</span>
                    <span class="stat-value" style="color: var(--success-color);">Optimal</span>
                </div>
            </div>

            <h3 style="margin-top: 2rem;"><i class="fas fa-tools"></i> Quick Actions</h3>
            <div style="display: flex; flex-direction: column; gap: 0.5rem; margin-top: 1rem;">
                <button class="btn btn-primary" onclick="showBulkImport()">
                    <i class="fas fa-upload"></i> Bulk Import
                </button>
                <button class="btn btn-outline" onclick="exportData()">
                    <i class="fas fa-download"></i> Export Data
                </button>
                <button class="btn btn-outline" onclick="showHistory()">
                    <i class="fas fa-history"></i> View History
                </button>
            </div>
        </aside>

        <main class="main-content">
            <div class="search-section">
                <div class="search-container">
                    <i class="fas fa-search search-icon"></i>
                    <input type="text" 
                           class="search-input" 
                           id="search-input"
                           placeholder="Search products by ID, description, or category..."
                           autocomplete="off">
                </div>
            </div>

            <div class="natural-language-section">
                <div class="nl-title">
                    <i class="fas fa-brain"></i>
                    Natural Language Commands
                </div>
                <input type="text" 
                       class="nl-input" 
                       id="nl-input"
                       placeholder="Try: 'Add 50 units to product 1015B' or 'Update description for 1020B to Premium Steel'"
                       autocomplete="off">
                <div class="nl-examples">
                    <div class="nl-example" onclick="setNLExample('Add 25 units to product 1015B')">Add 25 units to product 1015B</div>
                    <div class="nl-example" onclick="setNLExample('Set description for 1020B to Premium Steel')">Set description for 1020B to Premium Steel</div>
                    <div class="nl-example" onclick="setNLExample('Increase inventory for 1025AW by 100 units')">Increase inventory for 1025AW by 100</div>
                </div>
                <button class="btn btn-success" onclick="processNaturalLanguage()">
                    <i class="fas fa-magic"></i> Process Command
                </button>
            </div>

            <div class="loading" id="loading">
                <div class="spinner"></div>
                <div>Processing your request...</div>
            </div>

            <div class="results-section" id="results-section">
                <div class="results-grid" id="results-grid">
                    <!-- Results will be populated here -->
                </div>
            </div>
        </main>
    </div>

    <!-- Update Modal -->
    <div class="modal" id="update-modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3 class="modal-title">Update Product</h3>
                <button class="close-btn" onclick="closeModal()">&times;</button>
            </div>
            <form id="update-form">
                <input type="hidden" id="update-product-id">
                <div class="form-group">
                    <label class="form-label">Product ID</label>
                    <input type="text" class="form-input" id="display-product-id" readonly>
                </div>
                <div class="form-group">
                    <label class="form-label">Description</label>
                    <input type="text" class="form-input" id="update-description">
                </div>
                <div class="form-group">
                    <label class="form-label">Quantity</label>
                    <input type="number" class="form-input" id="update-quantity" step="0.01">
                </div>
                <div class="form-group">
                    <label class="form-label">Notes</label>
                    <textarea class="form-input" id="update-notes" rows="3"></textarea>
                </div>
                <div style="display: flex; gap: 1rem; justify-content: flex-end; margin-top: 1.5rem;">
                    <button type="button" class="btn btn-outline" onclick="closeModal()">Cancel</button>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-save"></i> Update Product
                    </button>
                </div>
            </form>
        </div>
    </div>

    <script>
        // Global variables
        let currentResults = [];
        let searchTimeout = null;

        // Initialize the application
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
            setupEventListeners();
            loadRecentItems();
        });

        // Set up event listeners
        function setupEventListeners() {
            // Search input
            document.getElementById('search-input').addEventListener('input', function(e) {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    performSearch(e.target.value);
                }, 300);
            });

            // Natural language input
            document.getElementById('nl-input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    processNaturalLanguage();
                }
            });

            // Update form
            document.getElementById('update-form').addEventListener('submit', function(e) {
                e.preventDefault();
                submitUpdate();
            });

            // Search input enter key
            document.getElementById('search-input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    performSearch(e.target.value);
                }
            });
        }

        // Load system statistics
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                document.getElementById('updates-today').textContent = data.updates_today;
                document.getElementById('item-count').textContent = `${data.items_loaded.toLocaleString()} Items`;
            } catch (error) {
                console.error('Failed to load stats:', error);
            }
        }

        // Perform search
        async function performSearch(query) {
            if (!query.trim()) {
                loadRecentItems();
                return;
            }

            showLoading(true);
            
            try {
                const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                const results = await response.json();
                
                displayResults(results);
            } catch (error) {
                console.error('Search failed:', error);
                showNotification('Search failed. Please try again.', 'error');
            } finally {
                showLoading(false);
            }
        }

        // Load recent items
        async function loadRecentItems() {
            showLoading(true);
            
            try {
                const response = await fetch('/api/search?q=');
                const results = await response.json();
                
                displayResults(results.slice(0, 10)); // Show top 10
            } catch (error) {
                console.error('Failed to load recent items:', error);
            } finally {
                showLoading(false);
            }
        }

        // Display search results
        function displayResults(results) {
            currentResults = results;
            const grid = document.getElementById('results-grid');
            
            if (!results || results.length === 0) {
                grid.innerHTML = `
                    <div style="text-align: center; padding: 3rem; color: var(--text-light);">
                        <i class="fas fa-search" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                        <p>No products found. Try a different search term.</p>
                    </div>
                `;
                return;
            }

            grid.innerHTML = results.map(item => `
                <div class="result-card" onclick="openUpdateModal('${item.product_id}')">
                    <div class="result-header">
                        <div class="product-id">${item.product_id}</div>
                        <div class="quantity-badge">${parseFloat(item.quantity).toLocaleString()} units</div>
                    </div>
                    <div class="result-description">${item.description || 'No description available'}</div>
                    <div class="result-actions">
                        <button class="btn btn-primary" onclick="event.stopPropagation(); openUpdateModal('${item.product_id}')">
                            <i class="fas fa-edit"></i> Update
                        </button>
                        <button class="btn btn-outline" onclick="event.stopPropagation(); quickAdd('${item.product_id}')">
                            <i class="fas fa-plus"></i> Quick Add
                        </button>
                    </div>
                </div>
            `).join('');
        }

        // Process natural language command
        async function processNaturalLanguage() {
            const input = document.getElementById('nl-input');
            const command = input.value.trim();
            
            if (!command) {
                showNotification('Please enter a command.', 'warning');
                return;
            }

            showLoading(true);
            
            try {
                const response = await fetch('/api/natural', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ command })
                });

                const result = await response.json();
                
                if (result.success) {
                    showNotification(result.data, 'success');
                    input.value = '';
                    loadStats(); // Refresh stats
                    
                    // If the command updated a specific product, refresh search
                    if (result.parsed && result.parsed.product_id) {
                        performSearch(result.parsed.product_id);
                    }
                } else {
                    showNotification(result.error || 'Command failed', 'error');
                }
            } catch (error) {
                console.error('Natural language processing failed:', error);
                showNotification('Failed to process command. Please try again.', 'error');
            } finally {
                showLoading(false);
            }
        }

        // Set natural language example
        function setNLExample(example) {
            document.getElementById('nl-input').value = example;
        }

        // Open update modal
        function openUpdateModal(productId) {
            const item = currentResults.find(r => r.product_id === productId);
            
            if (item) {
                document.getElementById('update-product-id').value = productId;
                document.getElementById('display-product-id').value = productId;
                document.getElementById('update-description').value = item.description || '';
                document.getElementById('update-quantity').value = item.quantity || '';
                document.getElementById('update-notes').value = '';
                
                document.getElementById('update-modal').style.display = 'block';
            }
        }

        // Close modal
        function closeModal() {
            document.getElementById('update-modal').style.display = 'none';
        }

        // Submit update
        async function submitUpdate() {
            const productId = document.getElementById('update-product-id').value;
            const description = document.getElementById('update-description').value;
            const quantity = document.getElementById('update-quantity').value;
            const notes = document.getElementById('update-notes').value;

            const updates = {};
            if (description) updates.description = description;
            if (quantity) updates.quantity = parseFloat(quantity);
            if (notes) updates.notes = notes;

            if (Object.keys(updates).length === 0) {
                showNotification('Please provide at least one update.', 'warning');
                return;
            }

            try {
                const response = await fetch('/api/update', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        product_id: productId,
                        updates: updates
                    })
                });

                const result = await response.json();

                if (result.success) {
                    showNotification(result.data, 'success');
                    closeModal();
                    loadStats();
                    
                    // Refresh the current search
                    const searchQuery = document.getElementById('search-input').value;
                    if (searchQuery) {
                        performSearch(searchQuery);
                    } else {
                        loadRecentItems();
                    }
                } else {
                    showNotification(result.error || 'Update failed', 'error');
                }
            } catch (error) {
                console.error('Update failed:', error);
                showNotification('Update failed. Please try again.', 'error');
            }
        }

        // Quick add function
        function quickAdd(productId) {
            const nlInput = document.getElementById('nl-input');
            nlInput.value = `Add 10 units to product ${productId}`;
            processNaturalLanguage();
        }

        // Show/hide loading
        function showLoading(show) {
            const loading = document.getElementById('loading');
            const results = document.getElementById('results-section');
            
            if (show) {
                loading.style.display = 'block';
                results.style.display = 'none';
            } else {
                loading.style.display = 'none';
                results.style.display = 'block';
            }
        }

        // Show notification
        function showNotification(message, type = 'success') {
            // Remove existing notifications
            const existing = document.querySelector('.notification');
            if (existing) {
                existing.remove();
            }

            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.textContent = message;
            
            document.body.appendChild(notification);
            
            // Show notification
            setTimeout(() => {
                notification.classList.add('show');
            }, 100);
            
            // Hide notification after 4 seconds
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => {
                    notification.remove();
                }, 300);
            }, 4000);
        }

        // Placeholder functions for sidebar actions
        function showBulkImport() {
            showNotification('Bulk import feature coming soon!', 'warning');
        }

        function exportData() {
            window.open('/api/export', '_blank');
        }

        function showHistory() {
            window.open('/api/history', '_blank');
        }

        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('update-modal');
            if (event.target === modal) {
                closeModal();
            }
        }

        // Auto-refresh stats every 30 seconds
        setInterval(loadStats, 30000);
    </script>
</body>
</html>
'''

def get_professional_interface():
    """Return the professional web interface HTML"""
    return PROFESSIONAL_HTML_TEMPLATE