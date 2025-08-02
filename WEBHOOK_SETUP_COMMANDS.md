# 📡 **WEBHOOK SETUP COMMANDS**

## **Your Webhook URL**
```
https://95891b50740f.ngrok-free.app/webhook/paradigm
```

## **STEP 1: Test Your Webhook URL**
Open in browser: https://95891b50740f.ngrok-free.app

You should see the Greenfield Inventory System.

## **STEP 2: Configure Webhook in Paradigm**

### **PowerShell Commands (Copy & Paste)**

```powershell
# 1. Authenticate first
$auth = Invoke-RestMethod -Uri "https://greenfieldapi.para-apps.com/api/Authenticate" `
  -Method POST `
  -Headers @{"x-api-key"="nVPsQFBteV&GEd7*8n0%RliVjksag8"} `
  -ContentType "application/json" `
  -Body '{"userName":"web_admin","password":"ChangeMe#123!"}'

# 2. Show the token (to verify it worked)
Write-Host "Token: $($auth.data.token)"

# 3. Create Inventory Update Webhook
$webhook1 = Invoke-RestMethod -Uri "https://greenfieldapi.para-apps.com/api/Webhook" `
  -Method POST `
  -Headers @{
    "Authorization"="Bearer $($auth.data.token)"
    "x-api-key"="nVPsQFBteV&GEd7*8n0%RliVjksag8"
  } `
  -ContentType "application/json" `
  -Body '{
    "address": "https://95891b50740f.ngrok-free.app/webhook/paradigm",
    "dataOperation": "UPDATE",
    "dataType": "INVENTORY",
    "httpType": "POST"
  }'

Write-Host "Webhook 1 Result: $webhook1"

# 4. Create Sales Order Webhook
$webhook2 = Invoke-RestMethod -Uri "https://greenfieldapi.para-apps.com/api/Webhook" `
  -Method POST `
  -Headers @{
    "Authorization"="Bearer $($auth.data.token)"
    "x-api-key"="nVPsQFBteV&GEd7*8n0%RliVjksag8"
  } `
  -ContentType "application/json" `
  -Body '{
    "address": "https://95891b50740f.ngrok-free.app/webhook/paradigm",
    "dataOperation": "CREATE",
    "dataType": "SALES_ORDER",
    "httpType": "POST"
  }'

Write-Host "Webhook 2 Result: $webhook2"
```

### **Alternative: cURL Commands**

```bash
# 1. Get auth token
curl -X POST "https://greenfieldapi.para-apps.com/api/Authenticate" \
  -H "x-api-key: nVPsQFBteV&GEd7*8n0%RliVjksag8" \
  -H "Content-Type: application/json" \
  -d '{"userName":"web_admin","password":"ChangeMe#123!"}'

# 2. Create webhook (use token from step 1)
curl -X POST "https://greenfieldapi.para-apps.com/api/Webhook" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "x-api-key: nVPsQFBteV&GEd7*8n0%RliVjksag8" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "https://95891b50740f.ngrok-free.app/webhook/paradigm",
    "dataOperation": "UPDATE",
    "dataType": "INVENTORY",
    "httpType": "POST"
  }'
```

## **STEP 3: Test Webhook**

1. **Watch ngrok window** - you'll see incoming requests
2. **Make a change in Paradigm** - update inventory quantity
3. **Check ngrok** - should show POST to /webhook/paradigm

## **TROUBLESHOOTING**

### **Ngrok shows "Tunnel not found"?**
- Ngrok URL changes each time you restart
- Get new URL: `curl http://localhost:4040/api/tunnels`
- Update webhook in Paradigm

### **Webhook not firing?**
- Check if ngrok is running
- Verify URL is correct (no typos)
- Try the PowerShell commands above

### **Getting 404 on webhook?**
- The 24/7 system doesn't have webhook endpoint built-in
- For now, watch ngrok window to see incoming webhooks
- We'll add proper handling when we move to Azure

## **NEXT STEPS**

Once webhooks are configured:
1. ✅ Test with real Paradigm changes
2. ✅ Verify ngrok shows the requests
3. ✅ Ready for Azure deployment!

---

**Need help?** Let me know what errors you see!