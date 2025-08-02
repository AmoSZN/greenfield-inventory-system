# 🔄 **PARADIGM API INTEGRATION GUIDE**

## **CURRENT STATUS**
- ✅ 39,184 products imported to local database
- ✅ API integration service created
- ⏳ Waiting for webhook configuration

## **WHAT I NEED FROM YOU**

### **1. Webhook Access**
**Question**: Can you access Paradigm's webhook configuration?
- Log into Paradigm Admin
- Look for: Settings → Integrations → Webhooks
- Or: API Settings → Event Notifications

### **2. Events to Monitor**
Which inventory events should trigger updates?
- **Sales Orders**: When items are sold
- **Purchase Orders**: When new stock arrives
- **Inventory Adjustments**: Manual quantity changes
- **Stock Transfers**: Between locations
- **Price Changes**: Update pricing

### **3. Your Public URL**
For webhooks to work, Paradigm needs to reach your system:
- **Option A**: Use ngrok (temporary URL)
- **Option B**: Port forwarding (if you have static IP)
- **Option C**: Cloud deployment

## **QUICK START**

### **Step 1: Start the API Integration Service**
```powershell
python paradigm_api_integration.py
```

### **Step 2: Configure Paradigm Webhook**
In Paradigm, set webhook URL to:
```
http://YOUR_PUBLIC_IP:5005/webhook/paradigm/inventory
```

### **Step 3: Test the Integration**
```powershell
# Test single product sync
curl -X POST http://localhost:5005/api/sync/product/1015AW

# Test health check
curl http://localhost:5005/health
```

## **API ENDPOINTS**

### **1. Webhook Receiver**
- **URL**: `/webhook/paradigm/inventory`
- **Method**: POST
- **Purpose**: Receives real-time updates from Paradigm

### **2. Manual Sync**
- **URL**: `/api/sync/product/<product_id>`
- **Method**: POST
- **Purpose**: Manually sync a single product

### **3. Bulk Sync**
- **URL**: `/api/sync/all`
- **Method**: POST
- **Purpose**: Sync all products (use sparingly)

## **WEBHOOK PAYLOAD FORMAT**

Paradigm should send webhooks in this format:
```json
{
  "eventType": "INVENTORY_UPDATE",
  "productId": "1015AW",
  "oldQuantity": 100,
  "newQuantity": 95,
  "timestamp": "2025-08-01T22:30:00Z",
  "source": "SALES_ORDER",
  "referenceId": "SO-12345"
}
```

## **NEXT STEPS**

1. **Tell me**: 
   - Can you access Paradigm webhook settings?
   - What's your preferred method for public access?
   - Which events should we monitor?

2. **I'll then**:
   - Configure the exact webhook format
   - Set up public access
   - Test the integration end-to-end

## **ALTERNATIVE: POLLING METHOD**

If webhooks aren't available, we can:
- Poll Paradigm API every X minutes
- Check for inventory changes
- Update local database
- Less real-time but still effective

**Which approach works best for your setup?**