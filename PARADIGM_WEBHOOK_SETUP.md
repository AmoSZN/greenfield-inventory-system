# Paradigm ERP Webhook Configuration

## Your Webhook URL
```
http://YOUR-PC-IP:5001/paradigm-webhook
```

To find your PC's IP:
```powershell
(Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"}).IPAddress
```

Example: `http://192.168.12.28:5001/paradigm-webhook`

## Steps in Paradigm ERP

1. **Login to Paradigm Admin Panel**
   - URL: https://greenfieldapi.para-apps.com
   - Use your admin credentials

2. **Navigate to Webhooks**
   - Settings → Integration → Webhooks
   - Click "Add New Webhook"

3. **Configure Webhook**
   - Name: "Label Printing Service"
   - URL: `http://YOUR-PC-IP:5001/paradigm-webhook`
   - Events: 
     - ✓ Order Created
     - ✓ Order Updated
     - ✓ Shipment Ready
   - Method: POST
   - Format: JSON

4. **Add Headers**
   - Content-Type: application/json
   - X-Webhook-Secret: 28DHqczoJRqMCz-kJPkTS89fM3LCJqpEmOZLsj4e73Y

5. **Test Connection**
   - Click "Test Webhook"
   - Check service logs:
   ```powershell
   Get-Content "C:\BarTenderIntegration\Logs\webhook_$(Get-Date -Format 'yyyyMMdd').log" -Tail 20
   ```

6. **Save and Enable**
   - Click "Save"
   - Toggle "Active" to ON

## Verify It's Working

### Method 1: Create Test Order in Paradigm
1. Create a new order in Paradigm
2. Watch for automatic label print

### Method 2: Check Logs
```powershell
# Watch logs in real-time
Get-Content "C:\BarTenderIntegration\Logs\webhook_$(Get-Date -Format 'yyyyMMdd').log" -Wait
```

### Method 3: Check Archive
```powershell
# See processed orders
Get-ChildItem "C:\BarTenderIntegration\Archive" -Filter "*.csv" | Select-Object -Last 5
```

## Troubleshooting

### Webhook Not Reaching Service
1. Check Windows Firewall:
   ```powershell
   New-NetFirewallRule -DisplayName "Greenfield Label Service" -Direction Inbound -LocalPort 5001 -Protocol TCP -Action Allow
   ```

2. Verify service is running:
   ```powershell
   Get-Service GreenfieldLabelService
   netstat -an | findstr :5001
   ```

### Labels Not Printing
1. Check BarTender queue
2. Verify printer is online
3. Check error logs:
   ```powershell
   Get-ChildItem "C:\BarTenderIntegration\ErrorReports" -Filter "*.txt" | Get-Content
   ``` 