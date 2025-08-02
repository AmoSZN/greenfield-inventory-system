# 🧪 **QUICK SYSTEM TEST GUIDE**

## **1️⃣ CHECK DASHBOARD**
Open in your browser: http://localhost:8000

**You should see:**
- ✅ Greenfield Inventory System header
- ✅ Search box for products
- ✅ Natural language update box
- ✅ Bulk import/export buttons

## **2️⃣ TEST PRODUCT SEARCH**
In the search box, try:
- "aluminum"
- "1010AG"
- "copper"

**Expected:** List of matching products with current quantities

## **3️⃣ TEST NATURAL LANGUAGE UPDATE**
In the update box, try these commands:
- "Add 50 units to product 1010AG"
- "Update 1015AW quantity to 300"
- "Set 1020B description to Premium Bronze Sheet"

**Expected:** Success message and updated values

## **4️⃣ CHECK NGROK**
Look at the ngrok window. You should see:
```
Session Status                online
Account                       your-email (Plan: Free)
Version                       3.x.x
Region                        United States (us)
Latency                       XXms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:8000
```

**Copy the https URL** (like https://abc123.ngrok-free.app)

## **5️⃣ CONFIGURE PARADIGM WEBHOOK**

### **Option A: Using Our Script**
```powershell
# Update the webhook URL in the script first
notepad configure_paradigm_webhooks.py
# Change LOCAL_WEBHOOK_URL to your ngrok URL

# Then run:
python configure_paradigm_webhooks.py
```

### **Option B: Manual cURL**
```powershell
# First authenticate
$auth = curl -X POST "https://greenfieldapi.para-apps.com/api/Authenticate" `
  -H "x-api-key: nVPsQFBteV&GEd7*8n0%RliVjksag8" `
  -H "Content-Type: application/json" `
  -d '{"userName": "web_admin", "password": "ChangeMe#123!"}' | ConvertFrom-Json

# Then create webhook (replace YOUR_NGROK_URL)
curl -X POST "https://greenfieldapi.para-apps.com/api/Webhook" `
  -H "Authorization: Bearer $($auth.data.token)" `
  -H "x-api-key: nVPsQFBteV&GEd7*8n0%RliVjksag8" `
  -H "Content-Type: application/json" `
  -d '{
    "address": "YOUR_NGROK_URL/webhook/paradigm",
    "dataOperation": "UPDATE",
    "dataType": "INVENTORY",
    "httpType": "POST"
  }'
```

## **6️⃣ TEST WEBHOOK**
1. Make a change in Paradigm ERP
2. Check ngrok window for incoming POST request
3. Check system logs for processing

## **🎯 SUCCESS INDICATORS**
- ✅ Dashboard loads
- ✅ Search returns products
- ✅ Updates work
- ✅ Ngrok shows public URL
- ✅ Webhooks configured
- ✅ Real-time updates working

## **❌ TROUBLESHOOTING**

### **Dashboard not loading?**
```powershell
# Check if running
netstat -an | findstr :8000

# Restart if needed
python inventory_system_24_7.py
```

### **Ngrok not working?**
```powershell
# Try direct command
.\ngrok http 8000
```

### **Webhook not firing?**
- Check ngrok is running
- Verify webhook URL includes /webhook/paradigm
- Check Paradigm webhook configuration

---

**Ready for Azure?** Once everything works locally, we'll deploy!