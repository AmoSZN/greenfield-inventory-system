# 📡 **MANUAL WEBHOOK SETUP GUIDE**

Since the Paradigm webhook API requires specific dataType values we haven't identified, here's how to set up webhooks manually:

## **🔧 OPTION 1: Paradigm Admin Panel**

### **Step 1: Access Paradigm Admin**
1. Log into Paradigm ERP as **web_admin**
2. Navigate to **System Settings** or **Integration** menu
3. Look for **Webhooks**, **API Callbacks**, or **Event Notifications**

### **Step 2: Configure Webhook**
**Webhook URL:** `https://95891b50740f.ngrok-free.app/webhook/paradigm`

**Events to Monitor:**
- ✅ Inventory Updates
- ✅ Sales Orders (Created/Updated)
- ✅ Purchase Orders (Created/Updated)
- ✅ Stock Adjustments
- ✅ Item Master Changes

### **Step 3: Test Configuration**
1. Make a change in Paradigm (update item description)
2. Check ngrok window for incoming webhook
3. Verify in our system at http://localhost:8000

---

## **🔧 OPTION 2: Contact Paradigm Support**

### **Information to Provide:**
```
Subject: Webhook API Configuration - Valid dataType Values

Hello Paradigm Support,

I'm integrating with the Paradigm API and need help with webhook configuration.

Current Issue:
- Authentication works (using /api/user/Auth/GetToken)
- Webhook creation fails with "DataType is not valid"

Request:
Please provide valid dataType values for webhook configuration.

Attempted Values (all failed):
- INVENTORY
- SALES_ORDER  
- PURCHASE_ORDER
- STOCK_ADJUSTMENT

API Endpoint: POST /api/Webhook
Payload: {
  "address": "https://example.com/webhook",
  "dataOperation": "UPDATE",
  "dataType": "???",
  "httpType": "POST"
}

Could you provide:
1. Valid dataType values
2. Valid dataOperation values
3. Example webhook payloads

Thank you!
```

---

## **🔧 OPTION 3: Alternative Integration**

### **Polling Approach**
Instead of webhooks, we can poll for changes:

```python
# Check for updates every 5 minutes
def poll_paradigm_changes():
    # Get recent updates from Paradigm
    # Compare with local database
    # Process any differences
```

### **File-based Integration**
If Paradigm can export change logs:
- Monitor a shared folder
- Process CSV/XML export files
- Import changes automatically

---

## **🎯 CURRENT STATUS**

### **✅ Working:**
- ✅ Ngrok tunnel active: `https://95891b50740f.ngrok-free.app`
- ✅ Webhook endpoint ready: `/webhook/paradigm`
- ✅ Authentication with Paradigm API
- ✅ System monitoring for incoming webhooks

### **⚠️ Pending:**
- Manual webhook configuration in Paradigm UI
- OR valid dataType values from Paradigm support

---

## **🧪 TEST WEBHOOK MANUALLY**

You can test the webhook endpoint directly:

```powershell
# Test webhook reception
curl -X POST "https://95891b50740f.ngrok-free.app/webhook/paradigm" `
  -H "Content-Type: application/json" `
  -d '{"test": "webhook", "productId": "1015B", "eventType": "INVENTORY_UPDATE"}'
```

**Expected Result:** Should appear in ngrok logs and system history.

---

## **📞 NEXT STEPS**

1. **Try Paradigm Admin Panel** - Look for webhook/integration settings
2. **Contact Paradigm Support** - Get valid API values
3. **Meanwhile** - System works great for manual updates!

The webhook integration will enable **real-time bidirectional sync** once configured.