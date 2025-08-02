#!/usr/bin/env python3
"""
Add bulk upload functionality to the inventory system
"""

import os
import shutil
from datetime import datetime

# Read the current inventory system
with open('inventory_system_24_7.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find where to insert the bulk upload routes (after the /api/update route)
insert_pos = content.find("@app.route('/api/update'")
if insert_pos == -1:
    print("❌ Could not find update route")
    exit(1)

# Find the end of the update route function
route_end = content.find("\n@app.route", insert_pos + 1)
if route_end == -1:
    route_end = content.find("\n\nif __name__", insert_pos)

# Bulk upload code to insert
bulk_code = '''

@app.route('/bulk-import-export')
async def bulk_import_export():
    """Bulk import/export page"""
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Bulk Import/Export - Greenfield Inventory</title>
    <style>
        body { font-family: Arial; margin: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        h1 { color: #2c3e50; }
        .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        button { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #2980b9; }
        .message { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        input[type="file"] { margin: 10px 0; }
        pre { background: #f8f9fa; padding: 10px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Bulk Import/Export</h1>
        <a href="/">← Back to Dashboard</a>
        
        <div class="section">
            <h2>📤 Import CSV</h2>
            <p>Upload a CSV file with columns: ProductID, Quantity, Description, Notes</p>
            <input type="file" id="csvFile" accept=".csv">
            <button onclick="uploadCSV()">Upload CSV</button>
            <div id="uploadResult"></div>
        </div>
        
        <div class="section">
            <h2>📥 Export Template</h2>
            <p>Download a template CSV file for bulk updates</p>
            <button onclick="downloadTemplate()">Download Template</button>
        </div>
        
        <div class="section">
            <h2>📋 CSV Format</h2>
            <pre>ProductID,Quantity,Description,Notes
1010AG,150,Aluminum Grade A,Updated via bulk import
1015AW,750,Aluminum Wire,Inventory adjustment</pre>
        </div>
    </div>
    
    <script>
        async function uploadCSV() {
            const fileInput = document.getElementById('csvFile');
            const file = fileInput.files[0];
            
            if (!file) {
                alert('Please select a CSV file');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch('/api/bulk-upload', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                const resultDiv = document.getElementById('uploadResult');
                if (result.success) {
                    resultDiv.innerHTML = `<div class="message success">
                        ✅ Upload successful!<br>
                        Processed: ${result.processed} items<br>
                        Success: ${result.success_count} items<br>
                        Failed: ${result.failed_count} items
                    </div>`;
                } else {
                    resultDiv.innerHTML = `<div class="message error">❌ ${result.error}</div>`;
                }
            } catch (error) {
                document.getElementById('uploadResult').innerHTML = 
                    `<div class="message error">❌ Upload failed: ${error.message}</div>`;
            }
        }
        
        function downloadTemplate() {
            const csv = 'ProductID,Quantity,Description,Notes\\n1010AG,150,Sample Product,Sample notes';
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'inventory_template.csv';
            a.click();
        }
    </script>
</body>
</html>'''

@app.route('/api/bulk-upload', methods=['POST'])
async def bulk_upload():
    """Handle bulk CSV upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        # Save uploaded file temporarily
        temp_path = os.path.join('uploads', f'temp_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
        os.makedirs('uploads', exist_ok=True)
        file.save(temp_path)
        
        # Process CSV
        results = {
            'processed': 0,
            'success_count': 0,
            'failed_count': 0,
            'errors': []
        }
        
        import csv
        with open(temp_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                results['processed'] += 1
                
                try:
                    product_id = row.get('ProductID', '').strip()
                    if not product_id:
                        results['failed_count'] += 1
                        results['errors'].append(f"Row {results['processed']}: Missing ProductID")
                        continue
                    
                    # Prepare updates
                    updates = {}
                    if row.get('Quantity'):
                        updates['quantity'] = int(row['Quantity'])
                    if row.get('Description'):
                        updates['description'] = row['Description']
                    if row.get('Notes'):
                        updates['notes'] = row['Notes']
                    
                    if not updates:
                        results['failed_count'] += 1
                        results['errors'].append(f"{product_id}: No updates specified")
                        continue
                    
                    # Update via Paradigm API
                    success = await paradigm_api.update_item_enhanced(
                        product_id,
                        new_quantity=updates.get('quantity'),
                        new_description=updates.get('description'),
                        notes=updates.get('notes')
                    )
                    
                    if success:
                        results['success_count'] += 1
                        
                        # Log to database
                        conn = sqlite3.connect(DB_FILE)
                        c = conn.cursor()
                        c.execute("""
                            INSERT INTO update_history 
                            (product_id, quantity_change, description_change, notes_change, reason, timestamp, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            product_id,
                            updates.get('quantity'),
                            updates.get('description'),
                            updates.get('notes'),
                            'Bulk CSV upload',
                            datetime.now().isoformat(),
                            'success'
                        ))
                        conn.commit()
                        conn.close()
                    else:
                        results['failed_count'] += 1
                        results['errors'].append(f"{product_id}: API update failed")
                        
                except Exception as e:
                    results['failed_count'] += 1
                    results['errors'].append(f"Row {results['processed']}: {str(e)}")
        
        # Clean up temp file
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'processed': results['processed'],
            'success_count': results['success_count'],
            'failed_count': results['failed_count'],
            'errors': results['errors'][:10]  # Limit errors shown
        })
        
    except Exception as e:
        logger.error(f"Bulk upload error: {e}")
        return jsonify({'success': False, 'error': str(e)})
'''

# Create backup
backup_name = f'inventory_system_24_7_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
shutil.copy('inventory_system_24_7.py', backup_name)
print(f"✅ Created backup: {backup_name}")

# Insert the bulk upload code
new_content = content[:route_end] + bulk_code + content[route_end:]

# Write the updated file
with open('inventory_system_24_7.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Added bulk upload functionality to inventory_system_24_7.py")
print("🔄 Please restart the inventory system to use the new features")