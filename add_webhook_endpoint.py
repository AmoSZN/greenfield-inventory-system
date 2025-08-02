#!/usr/bin/env python3
"""
Add webhook endpoint to inventory_system_24_7.py
"""

print("📝 Adding webhook endpoint to inventory system...")

# Read the current file
with open('inventory_system_24_7.py', 'r') as f:
    content = f.read()

# Find where to insert the webhook route (after other routes)
insert_position = content.find('@app.route("/api/system/status")')

if insert_position == -1:
    print("❌ Could not find insertion point")
    exit(1)

# Webhook endpoint code
webhook_code = '''
@app.route('/webhook/paradigm', methods=['POST', 'GET'])
def paradigm_webhook():
    """Handle incoming webhooks from Paradigm ERP"""
    if request.method == 'GET':
        # For testing
        return jsonify({"status": "Webhook endpoint active", "timestamp": datetime.now().isoformat()})
    
    try:
        # Log the webhook
        webhook_data = request.get_json()
        print(f"📨 Webhook received: {webhook_data}")
        
        # Store webhook in history
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO update_history (product_id, action, old_value, new_value, timestamp, source)
            VALUES (?, ?, ?, ?, ?, ?)''', (
            webhook_data.get('productId', 'UNKNOWN'),
            f"WEBHOOK: {webhook_data.get('eventType', 'UNKNOWN')}",
            json.dumps(webhook_data),
            'Webhook received',
            datetime.now().isoformat(),
            'Paradigm Webhook'
        ))
        conn.commit()
        conn.close()
        
        # Process based on event type
        event_type = webhook_data.get('eventType', '').upper()
        
        if 'INVENTORY' in event_type:
            # Handle inventory update
            product_id = webhook_data.get('productId')
            if product_id:
                # You could trigger a sync here
                print(f"🔄 Inventory update for: {product_id}")
        
        elif 'SALES' in event_type:
            # Handle sales order
            print(f"💰 Sales order webhook: {webhook_data}")
        
        elif 'PURCHASE' in event_type:
            # Handle purchase order
            print(f"📦 Purchase order webhook: {webhook_data}")
        
        return jsonify({
            "status": "success",
            "message": "Webhook processed",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

'''

# Insert the webhook code
new_content = content[:insert_position] + webhook_code + '\n' + content[insert_position:]

# Write back
with open('inventory_system_24_7.py', 'w') as f:
    f.write(new_content)

print("✅ Webhook endpoint added!")
print("\n⚠️  IMPORTANT: Restart the inventory system:")
print("   1. Close the current system (Ctrl+C)")
print("   2. Run: python inventory_system_24_7.py")
print("\n📝 Your webhook URL:")
print("   https://95891b50740f.ngrok-free.app/webhook/paradigm")