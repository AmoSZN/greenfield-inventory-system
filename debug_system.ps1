# Greenfield Metal Sales - Complete System Debug Script
# This script systematically tests each component

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "GREENFIELD METAL SALES - SYSTEM DEBUG PROCESS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Clean State
Write-Host "[STEP 1] Ensuring Clean State..." -ForegroundColor Yellow
Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "✓ All Python processes stopped" -ForegroundColor Green
Write-Host ""

# Step 2: Test BarTender Direct
Write-Host "[STEP 2] Testing BarTender Direct..." -ForegroundColor Yellow
Write-Host "Running direct BarTender test..."
$bartenderTest = & python test_bartender_direct.py 2>&1 | Out-String
if ($bartenderTest -match "Print command executed successfully") {
    Write-Host "✓ BarTender direct test PASSED" -ForegroundColor Green
} else {
    Write-Host "✗ BarTender direct test FAILED" -ForegroundColor Red
    Write-Host "Error details:" -ForegroundColor Red
    Write-Host $bartenderTest
}
Write-Host ""

# Step 3: Test Simple Webhook (No AI)
Write-Host "[STEP 3] Testing Simple Webhook Mode..." -ForegroundColor Yellow
Write-Host "Starting webhook_simple_print.py..."
Start-Process python -ArgumentList "webhook_simple_print.py" -WindowStyle Hidden
Start-Sleep -Seconds 5

# Test webhook health
try {
    $health = Invoke-RestMethod -Uri "http://localhost:5001/health" -TimeoutSec 5
    Write-Host "✓ Webhook service is running" -ForegroundColor Green
    
    # Test print
    Write-Host "Testing print functionality..."
    $printTest = Invoke-RestMethod -Uri "http://localhost:5001/test-print" -TimeoutSec 30
    if ($printTest.status -eq "success") {
        Write-Host "✓ Simple webhook print test PASSED" -ForegroundColor Green
        Write-Host "  Order printed: $($printTest.order.orderNumber)" -ForegroundColor Gray
    } else {
        Write-Host "✗ Simple webhook print test FAILED" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Simple webhook test FAILED" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}

Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host ""

# Step 4: Test Integrated System
Write-Host "[STEP 4] Testing Integrated System (Scanner + AI)..." -ForegroundColor Yellow
Write-Host "Starting main_app.py..."
Start-Process python -ArgumentList "main_app.py" -WindowStyle Hidden
Start-Sleep -Seconds 5

# Test system status
try {
    $status = Invoke-RestMethod -Uri "http://localhost:5001/system/status" -TimeoutSec 5
    if ($status.modules.scanner -eq "active" -and $status.modules.ai -eq "active") {
        Write-Host "✓ Both modules active" -ForegroundColor Green
        Write-Host "  Scanner: $($status.modules.scanner)" -ForegroundColor Gray
        Write-Host "  AI: $($status.modules.ai)" -ForegroundColor Gray
    } else {
        Write-Host "✗ Module activation FAILED" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Integrated system test FAILED" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}
Write-Host ""

# Step 5: Test AI Features
Write-Host "[STEP 5] Testing AI Features..." -ForegroundColor Yellow

# Send normal order
Write-Host "Sending normal order..."
$normalOrder = @{
    orderNumber = "NORMAL-001"
    customerPO = "PO-12345"
    billToCompany = "Regular Customer Inc"
    shipToCompany = "Regular Customer Inc"
    products = @(
        @{
            productId = "STEEL-001"
            description = "Steel Plate 1/4 inch"
            quantity = 50
        }
    )
} | ConvertTo-Json

try {
    $normalResult = Invoke-RestMethod -Method Post -Uri "http://localhost:5001/paradigm-webhook" -Body $normalOrder -ContentType "application/json" -TimeoutSec 30
    Write-Host "✓ Normal order processed" -ForegroundColor Green
} catch {
    Write-Host "✗ Normal order failed: $_" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# Send anomaly order
Write-Host "Sending anomaly order..."
$anomalyOrder = @{
    orderNumber = "ANOMALY-001"
    customerPO = "SUSPICIOUS-PO"
    billToCompany = "Never Seen Before Corp"
    shipToCompany = "Unknown Location LLC"
    products = @(
        @{
            productId = "WEIRD-999"
            description = "Unknown Product"
            quantity = 99999
        }
    )
} | ConvertTo-Json

try {
    $anomalyResult = Invoke-RestMethod -Method Post -Uri "http://localhost:5001/paradigm-webhook" -Body $anomalyOrder -ContentType "application/json" -TimeoutSec 30
    Write-Host "✓ Anomaly order processed" -ForegroundColor Green
} catch {
    Write-Host "✗ Anomaly order failed: $_" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# Check AI report
Write-Host "Checking AI analysis report..."
try {
    $aiReport = Invoke-RestMethod -Uri "http://localhost:5001/system/ai/report" -TimeoutSec 5
    Write-Host "✓ AI Report Retrieved" -ForegroundColor Green
    Write-Host "  Total SKUs tracked: $($aiReport.total_skus)" -ForegroundColor Gray
    Write-Host "  Order velocity: $($aiReport.order_velocity)" -ForegroundColor Gray
} catch {
    Write-Host "✗ AI report failed: $_" -ForegroundColor Red
}

Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host ""

# Step 6: Check Logs
Write-Host "[STEP 6] Checking Logs..." -ForegroundColor Yellow
$today = Get-Date -Format "yyyyMMdd"
$logFiles = @(
    "C:\BarTenderIntegration\Logs\webhook_simple_$today.log"
    "C:\BarTenderIntegration\Logs\scanner_$today.log"
    "C:\BarTenderIntegration\Logs\ai_$today.log"
)

foreach ($logFile in $logFiles) {
    if (Test-Path $logFile) {
        Write-Host "✓ Found log: $(Split-Path $logFile -Leaf)" -ForegroundColor Green
        $errors = Get-Content $logFile | Select-String "ERROR" | Select-Object -Last 3
        if ($errors) {
            Write-Host "  Recent errors:" -ForegroundColor Yellow
            $errors | ForEach-Object { Write-Host "    $_" -ForegroundColor Red }
        } else {
            Write-Host "  No errors found" -ForegroundColor Gray
        }
    } else {
        Write-Host "- Log not found: $(Split-Path $logFile -Leaf)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "DEBUG PROCESS COMPLETE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. If all tests passed → Run 'install_as_service.bat' as Administrator"
Write-Host "2. If BarTender failed → Check BarTender installation and templates"
Write-Host "3. If AI failed → Check config.json AI settings"
Write-Host "4. If webhook failed → Check port 5001 availability"
Write-Host "" 