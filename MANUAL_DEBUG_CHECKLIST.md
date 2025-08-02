# Manual Debug Checklist - Exact Commands

## Pre-Flight Checks

### 1. Kill All Python Processes
```powershell
Get-Process python* | Stop-Process -Force -ErrorAction SilentlyContinue
```

### 2. Check Port Availability
```powershell
netstat -an | findstr :5001
```
Should return nothing if port is free.

## Component Tests

### Test 1: BarTender Direct (No Flask/Web)
```powershell
python test_bartender_direct.py
```
✅ **PASS**: You see "Print command executed successfully"
❌ **FAIL**: Any error messages

### Test 2: Simple Webhook (No AI)
```powershell
# Terminal 1 - Start service
python webhook_simple_print.py

# Terminal 2 - Test it
Invoke-RestMethod -Uri "http://localhost:5001/health"
Invoke-RestMethod -Uri "http://localhost:5001/test-print"
```
✅ **PASS**: Returns success status
❌ **FAIL**: 500 error or timeout

### Test 3: Full Integration Test
```powershell
python test_integration.py
```
✅ **PASS**: "5 passed, 0 failed"
❌ **FAIL**: Any test failures

### Test 4: Integrated System (Scanner + AI)
```powershell
# Terminal 1 - Start integrated system
python main_app.py

# Terminal 2 - Check status
Invoke-RestMethod -Uri "http://localhost:5001/system/status" | ConvertTo-Json

# Terminal 2 - Test print with AI monitoring
Invoke-RestMethod -Uri "http://localhost:5001/test-print" | ConvertTo-Json
```
✅ **PASS**: Both modules show "active", print succeeds
❌ **FAIL**: Modules inactive or errors

### Test 5: AI Anomaly Detection
```powershell
# With main_app.py running, send anomaly
$anomaly = @{
    orderNumber = "ANOMALY-TEST"
    customerPO = "WEIRD-PO"
    billToCompany = "Unknown Corp"
    shipToCompany = "Unknown Corp"
    products = @(@{
        productId = "XXX-999"
        description = "Strange Item"
        quantity = 99999
    })
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:5001/paradigm-webhook" -Body $anomaly -ContentType "application/json"
```
✅ **PASS**: Order processes, check logs for AI detection
❌ **FAIL**: 500 error or no response

## Log Locations to Check

### Today's Logs
```powershell
$today = Get-Date -Format "yyyyMMdd"

# View webhook logs
Get-Content "C:\BarTenderIntegration\Logs\webhook_simple_$today.log" -Tail 20

# View scanner logs  
Get-Content "C:\BarTenderIntegration\Logs\scanner_$today.log" -Tail 20

# View AI logs
Get-Content "C:\BarTenderIntegration\Logs\ai_$today.log" -Tail 20

# Check for errors
Get-Content "C:\BarTenderIntegration\Logs\*$today.log" | Select-String "ERROR"
```

## Common Issues & Fixes

### Issue: "CoInitialize has not been called"
✅ **FIX**: Already fixed in webhook_simple_print.py using CLI method

### Issue: Port 5001 in use
```powershell
# Find what's using port
netstat -ano | findstr :5001
# Kill the process using the PID shown
Stop-Process -Id [PID] -Force
```

### Issue: BarTender timeout
✅ **FIX**: Check if BarTender window is open waiting for input
```powershell
Get-Process BarTend* | Stop-Process -Force
```

### Issue: Template not found
```powershell
# Check template exists
Test-Path "C:\BarTenderIntegration\Templates\PackingList.btw"
Test-Path "Templates\PackingList.btw"
```

### Issue: AI module errors
```powershell
# Temporarily disable AI
$config = Get-Content config.json | ConvertFrom-Json
$config.ai.enabled = $false
$config | ConvertTo-Json -Depth 10 | Set-Content config.json
```

## Quick Health Check Script
```powershell
# Run this for a quick system check
Write-Host "Checking system health..." -ForegroundColor Cyan

# Check BarTender
if (Test-Path "C:\Program Files\Seagull\BarTender 11.4\BarTend.exe") {
    Write-Host "✓ BarTender installed" -ForegroundColor Green
} else {
    Write-Host "✗ BarTender not found" -ForegroundColor Red
}

# Check directories
@("Data", "Archive", "ErrorReports", "Logs") | ForEach-Object {
    if (Test-Path "C:\BarTenderIntegration\$_") {
        Write-Host "✓ $_ directory exists" -ForegroundColor Green
    } else {
        Write-Host "✗ $_ directory missing" -ForegroundColor Red
    }
}

# Check templates
if (Test-Path "Templates\PackingList.btw") {
    Write-Host "✓ Template found" -ForegroundColor Green
} else {
    Write-Host "✗ Template missing" -ForegroundColor Red
}

# Check Python
python --version
if ($?) {
    Write-Host "✓ Python installed" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found" -ForegroundColor Red
}
``` 