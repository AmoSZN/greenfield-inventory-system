# 🚀 FINAL DEPLOYMENT STEPS - GREENFIELD LABEL SERVICE

## Prerequisites Completed ✅
- All tests passed (5/5)
- BarTender working
- Webhook service tested
- AI integration active
- New Paradigm credentials configured

## Step 1: Start Webhook Service (Test Mode)
```powershell
# Terminal 1 - Start the service
python webhook_simple_print.py
```

## Step 2: Verify Everything Works
```powershell
# Terminal 2 - Run verification
python verify_paradigm_integration.py
```

Expected output:
- ✓ API Connection
- ✓ Order Lookup  
- ✓ Webhook Service
- ✓ Webhook Config
- ✓ End-to-End Test

## Step 3: Configure Paradigm Webhook
```powershell
# Terminal 2 - Configure webhook in Paradigm
python configure_paradigm_webhook.py
```

Follow prompts:
- Local IP will be detected (e.g., 192.168.12.28)
- Webhook URL: http://192.168.12.28:5001/paradigm-webhook
- Get fresh token? (y/n): **y** (recommended)

## Step 4: Deploy as Windows Service
```powershell
# Close Terminal 1 (Ctrl+C)
# Open PowerShell as Administrator

cd "C:\Users\mattm\OneDrive\Greenfield Metal Sales\Barcode Scanner"
.\install_as_service.bat
```

## Step 5: Start Monitoring
```powershell
# Regular PowerShell
.\monitor_dashboard.ps1
```

## Step 6: Test with Real Order
1. Create order in Paradigm ERP
2. Watch monitoring dashboard
3. Verify label prints

## What I Still Need From You:

### 1. **Webhook Data Structure**
I need to know what fields Paradigm sends in the webhook payload. Can you:
- Create a test order in Paradigm
- Check the webhook logs to see the exact JSON structure
- Or provide a sample webhook payload

Example of what I'm looking for:
```json
{
  "orderNumber": "ORD-12345",
  "customerPO": "PO-98765",
  "shipToCompany": "ABC Corp",
  "billToCompany": "ABC Corp",
  "shipDate": "2025-07-30",
  "products": [
    {
      "productId": "STEEL-001",
      "description": "Steel Plate",
      "quantity": 100
    }
  ]
}
```

### 2. **BarTender Template Fields**
What fields does your PackingList.btw template expect? The current code creates CSV with:
- OrderNumber
- CustomerPO
- ShipToCompany
- BillToCompany
- ShipDate

Are these correct? Are there additional fields needed?

### 3. **Firewall Configuration**
If Paradigm is cloud-based and needs to reach your local PC:
```powershell
# Open firewall port
New-NetFirewallRule -DisplayName "Greenfield Label Service" `
  -Direction Inbound -LocalPort 5001 -Protocol TCP -Action Allow
```

You might also need:
- Port forwarding on your router
- Dynamic DNS if your IP changes
- Or use a tunneling service like ngrok

## Quick Commands Reference

### Check Service Status
```powershell
Get-Service GreenfieldLabelService
```

### Restart Service
```powershell
Restart-Service GreenfieldLabelService
```

### View Today's Logs
```powershell
Get-Content "C:\BarTenderIntegration\Logs\webhook_$(Get-Date -Format 'yyyyMMdd').log" -Tail 50
```

### Test Print
```powershell
Invoke-RestMethod -Uri "http://localhost:5001/test-print"
```

## 🎯 You're 90% Done!

Once you provide:
1. Sample webhook JSON from Paradigm
2. Confirm BarTender template fields
3. Ensure network connectivity

The system will be **100% production ready**! 