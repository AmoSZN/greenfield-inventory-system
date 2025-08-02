# 🔧 **PARADIGM WEBHOOK CONFIGURATION GUIDE**

## **STEP 1: Configure Webhooks in Paradigm**

### **Access Webhook Settings**
1. Log into Paradigm as Admin
2. Navigate to: **System → API Configuration → Webhooks**
   - Or: **Settings → Integrations → Event Notifications**
   - Or: **Admin → External Systems → Webhooks**

### **Create New Webhook**
Click "Add Webhook" or "New Integration" and configure:

**Webhook Details:**
- **Name**: Greenfield Inventory Sync
- **URL**: `https://greenfield-inventory-api.azurewebsites.net/webhook/paradigm`
- **Method**: POST
- **Content Type**: application/json
- **Authentication**: Bearer Token (optional)

**Events to Subscribe:**
- ✅ Inventory Update
- ✅ Stock Adjustment
- ✅ Sales Order Completed
- ✅ Purchase Order Received
- ✅ Stock Transfer
- ✅ Inventory Count
- ✅ Product Created
- ✅ Product Modified
- ✅ Price Change

**Payload Format:**
```json
{
  "event_type": "INVENTORY_UPDATE",
  "product_id": "${ProductID}",
  "old_quantity": ${OldQuantity},
  "new_quantity": ${NewQuantity},
  "timestamp": "${EventTimestamp}",
  "source": "${EventSource}",
  "reference_id": "${ReferenceNumber}",
  "user": "${UserName}",
  "location": "${Location}"
}
```

**Retry Policy:**
- Max Retries: 3
- Retry Interval: 30 seconds
- Timeout: 10 seconds

## **STEP 2: Test Webhook Configuration**

### **In Paradigm:**
1. Find "Test Webhook" button
2. Select a test product (e.g., "1015AW")
3. Send test event
4. Check response status

### **Expected Response:**
```json
{
  "status": "accepted",
  "event_id": "SO-12345"
}
```

## **STEP 3: Configure Paradigm API Access**

### **API Settings:**
Ensure these are enabled:
- ✅ Items API - Read/Write
- ✅ Inventory API - Read/Write
- ✅ Webhooks - Outbound Enabled
- ✅ Real-time Events - Enabled

### **Security:**
1. **Whitelist Azure IP**: Add Azure App Service outbound IPs
2. **API Rate Limits**: Set to 1000 requests/minute
3. **Webhook Secret**: Generate and add to both systems

## **STEP 4: Field Mappings**

Map Paradigm fields to webhook payload:

| Paradigm Field | Webhook Field | Type |
|----------------|---------------|------|
| strProductID | product_id | string |
| decUnitsInStock | new_quantity | number |
| strLocation | location | string |
| dtmLastModified | timestamp | datetime |
| strUserName | user | string |

## **STEP 5: Enable Real-time Sync**

### **In Paradigm:**
1. Go to **System → Real-time Settings**
2. Enable:
   - ✅ Push inventory changes immediately
   - ✅ Include all locations
   - ✅ Send zero quantity updates
   - ✅ Include pending transactions

### **Sync Rules:**
Configure business rules:
- **Minimum Change**: 1 unit (or 0 for all changes)
- **Excluded Products**: None
- **Sync Direction**: Bidirectional
- **Conflict Resolution**: Last Write Wins

## **STEP 6: Monitor Webhook Activity**

### **In Paradigm:**
- **Path**: Reports → API → Webhook Log
- **Check**:
  - Successful deliveries
  - Failed attempts
  - Response times
  - Error messages

### **In Azure:**
- **Application Insights**: Monitor incoming webhooks
- **Log Analytics**: Query webhook events
- **Alerts**: Set up for failures

## **TROUBLESHOOTING**

### **Webhook Not Firing:**
1. Check event subscriptions
2. Verify URL is accessible
3. Check firewall rules
4. Review Paradigm logs

### **Authentication Errors:**
1. Verify API key in webhook headers
2. Check bearer token if used
3. Ensure web_admin has webhook permissions

### **Data Not Syncing:**
1. Check field mappings
2. Verify product IDs match
3. Review transformation rules
4. Check Azure logs

## **TESTING CHECKLIST**

- [ ] Create test sales order
- [ ] Verify webhook fires
- [ ] Check Azure receives event
- [ ] Confirm local DB updates
- [ ] Verify Paradigm shows update
- [ ] Test bulk operations
- [ ] Test error scenarios

## **SUPPORT CONTACTS**

**Paradigm Support:**
- API Issues: api-support@paradigm.com
- Webhook Help: integrations@paradigm.com

**Your Azure Resources:**
- App URL: https://greenfield-inventory-api.azurewebsites.net
- Health Check: https://greenfield-inventory-api.azurewebsites.net/health
- API Docs: https://greenfield-inventory-api.azurewebsites.net/docs

---

**Ready to configure?** Let me know what you find in the Paradigm webhook settings!