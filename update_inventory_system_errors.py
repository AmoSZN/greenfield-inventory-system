#!/usr/bin/env python3
"""
Update the inventory system to show proper error messages for sync failures
"""

import re

print("🔧 Updating Inventory System Error Handling")
print("=" * 60)

# Read the current inventory system
with open('inventory_system_24_7.py', 'r') as f:
    content = f.read()

# Find the update_inventory method and update it
old_method = '''    def update_inventory(self, product_id, updates):
        """Update inventory item in Paradigm ERP and local database"""
        if not self.ensure_authenticated():
            return False, "Authentication failed"
        
        try:
            # Build update payload
            update_payload = {
                "strProductID": product_id,
                "dtmLastModified": datetime.now().isoformat()
            }
            
            # Add fields to update
            if 'quantity' in updates and updates['quantity']:
                update_payload["decUnitsInStock"] = float(updates['quantity'])
            
            if 'description' in updates and updates['description']:
                update_payload["memDescription"] = updates['description']
            
            if 'notes' in updates and updates['notes']:
                update_payload["strNotes"] = updates['notes']
            
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
            
            if response.status_code == 200:
                # Update local database
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                
                # Update item
                if 'quantity' in updates:
                    c.execute('UPDATE items SET quantity = ? WHERE product_id = ?',
                              (updates['quantity'], product_id))
                
                if 'description' in updates:
                    c.execute('UPDATE items SET description = ? WHERE product_id = ?',
                              (updates['description'], product_id))
                
                # Update access count
                c.execute('UPDATE items SET times_accessed = times_accessed + 1 WHERE product_id = ?',
                          (product_id,))
                
                # Add to history
                for field, value in updates.items():
                    c.execute('''INSERT INTO update_history 
                                 (product_id, field_updated, new_value, updated_at)
                                 VALUES (?, ?, ?, ?)''',
                              (product_id, field, str(value), datetime.now()))
                
                conn.commit()
                conn.close()
                
                return True, response.json()
            else:
                return False, f"Update failed: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Update error: {str(e)}")
            return False, str(e)'''

new_method = '''    def update_inventory(self, product_id, updates):
        """Update inventory item in Paradigm ERP and local database"""
        if not self.ensure_authenticated():
            return False, "Authentication failed"
        
        try:
            # Build update payload
            update_payload = {
                "strProductID": product_id,
                "dtmLastModified": datetime.now().isoformat()
            }
            
            # Track which fields can be updated vs read-only
            paradigm_updateable = {}
            local_only_updates = {}
            
            # Add fields that CAN be updated in Paradigm
            if 'description' in updates and updates['description']:
                paradigm_updateable["memDescription"] = updates['description']
            
            if 'notes' in updates and updates['notes']:
                paradigm_updateable["strNotes"] = updates['notes']
            
            # Quantity updates are LOCAL ONLY (Paradigm inventory is read-only)
            if 'quantity' in updates and updates['quantity']:
                local_only_updates['quantity'] = updates['quantity']
            
            # Update Paradigm with updateable fields
            paradigm_success = True
            paradigm_error = None
            
            if paradigm_updateable:
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
                    paradigm_error = f"Paradigm update failed: {response.status_code}"
            
            # Always update local database
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            # Update all fields locally (for tracking)
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
                             (product_id, field_updated, new_value, updated_at, status)
                             VALUES (?, ?, ?, ?, ?)''',
                          (product_id, field, str(value), datetime.now(), status))
            
            conn.commit()
            conn.close()
            
            # Return appropriate message
            if local_only_updates and paradigm_updateable:
                if paradigm_success:
                    return True, f"✅ Description/Notes updated in Paradigm. ⚠️ Quantity updated locally only (Paradigm inventory is read-only)"
                else:
                    return False, f"❌ Paradigm update failed: {paradigm_error}. ✅ Local updates saved."
            elif local_only_updates:
                return True, f"⚠️ Quantity updated locally only. Paradigm inventory quantities are read-only and require inventory transactions (Purchase Orders, Adjustments, etc.)"
            elif paradigm_updateable:
                if paradigm_success:
                    return True, "✅ Successfully updated in Paradigm ERP"
                else:
                    return False, f"❌ Paradigm update failed: {paradigm_error}"
            else:
                return False, "No valid updates provided"
                
        except Exception as e:
            logger.error(f"Update error: {str(e)}")
            return False, f"System error: {str(e)}"'''

# Replace the method
if old_method in content:
    content = content.replace(old_method, new_method)
    print("✅ Updated update_inventory method")
else:
    print("❌ Could not find update_inventory method to replace")

# Also need to update the database schema to include status column
schema_update = '''
# Update database schema to include status tracking
def update_database_schema():
    """Add status column to update_history table"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if status column exists
    c.execute("PRAGMA table_info(update_history)")
    columns = [column[1] for column in c.fetchall()]
    
    if 'status' not in columns:
        c.execute('ALTER TABLE update_history ADD COLUMN status TEXT DEFAULT "SUCCESS"')
        conn.commit()
        print("✅ Added status column to update_history table")
    
    conn.close()
'''

# Add the schema update function before the init_db function
init_db_pos = content.find('def init_db():')
if init_db_pos != -1:
    content = content[:init_db_pos] + schema_update + '\n' + content[init_db_pos:]
    
    # Also call it in init_db
    content = content.replace(
        'def init_db():',
        '''def init_db():
    """Initialize database and update schema"""
    update_database_schema()'''
    )
    print("✅ Added database schema update")

# Write the updated file
with open('inventory_system_24_7.py', 'w') as f:
    f.write(content)

print("\n✅ Inventory system updated!")
print("\n📋 Changes made:")
print("1. ✅ Quantity updates are now LOCAL ONLY with clear warnings")
print("2. ✅ Description/Notes updates still sync to Paradigm")
print("3. ✅ Clear error messages explain why inventory sync fails")
print("4. ✅ History tracking includes sync status")
print("5. ✅ Database schema updated to track sync status")

print("\n🔄 Restart the inventory system to apply changes:")
print("   1. Stop current system (Ctrl+C)")
print("   2. Run: python inventory_system_24_7.py")
print("\n🧪 Test the fix:")
print("   1. Try updating 1015B quantity to 1000")
print("   2. Should see clear warning about local-only update")
print("   3. Description updates should still work with Paradigm")