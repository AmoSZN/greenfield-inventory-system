# 🏷️ GREENFIELD LABEL PRINTING - OPERATOR GUIDE

## ✅ Normal Operation
When everything is working correctly:
- **Labels print automatically** when orders are created in Paradigm
- **No action needed** from you!

## 🔍 Quick Status Check
Open PowerShell and run:
```
Get-Service GreenfieldLabelService
```
Should show: **Status: Running**

## 🚨 Common Issues & Fixes

### ❌ Labels Not Printing

1. **Check if service is running:**
   ```powershell
   Get-Service GreenfieldLabelService
   ```
   
2. **If stopped, restart it:**
   ```powershell
   Restart-Service GreenfieldLabelService
   ```

3. **Check printer:**
   - Is printer turned on?
   - Any paper jams?
   - Labels loaded correctly?

### ❌ BarTender Error Window

If BarTender shows an error:
1. Click OK/Close on any error dialogs
2. Run this to clear stuck BarTender:
   ```powershell
   Get-Process BarTend* | Stop-Process -Force
   ```

### 📋 Manual Label Reprint

To reprint a specific order:
```powershell
cd "C:\Users\mattm\OneDrive\Greenfield Metal Sales\Barcode Scanner"
python order_lookup_interface.ps1
```
Then enter the order number when prompted.

## 📞 Emergency Contacts

If the above doesn't work:

1. **IT Support**: [Your IT contact]
2. **Check monitoring dashboard**:
   ```powershell
   .\monitor_dashboard.ps1
   ```

## 🔄 Daily Maintenance

**Every morning:**
1. Print a test label:
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5001/test-print"
   ```
2. Clear old files (monthly):
   ```powershell
   # This removes files older than 30 days
   Get-ChildItem "C:\BarTenderIntegration\Archive" -Filter "*.csv" | 
     Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | 
     Remove-Item
   ```

## 💡 Tips
- Keep BarTender closed when not manually printing
- Service runs in background - no window needed
- Logs are in: `C:\BarTenderIntegration\Logs\`

---
*Last Updated: July 2025* 