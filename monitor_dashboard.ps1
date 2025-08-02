# Greenfield Metal Sales - Production Monitoring Dashboard
# Run this in a separate PowerShell window to monitor the system

$host.UI.RawUI.WindowTitle = "Greenfield Label Service Monitor"

while ($true) {
    Clear-Host
    
    # Header
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "GREENFIELD LABEL SERVICE - MONITORING DASHBOARD" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White
    Write-Host ""
    
    # Service Status
    Write-Host "SERVICE STATUS" -ForegroundColor Yellow
    $service = Get-Service GreenfieldLabelService -ErrorAction SilentlyContinue
    if ($service) {
        $color = if ($service.Status -eq 'Running') { 'Green' } else { 'Red' }
        Write-Host "  Status: $($service.Status)" -ForegroundColor $color
        Write-Host "  Startup: $($service.StartType)" -ForegroundColor Gray
    } else {
        Write-Host "  Status: NOT INSTALLED" -ForegroundColor Red
    }
    Write-Host ""
    
    # Network Status
    Write-Host "NETWORK STATUS" -ForegroundColor Yellow
    $listening = netstat -an | findstr ":5001.*LISTENING"
    if ($listening) {
        Write-Host "  Port 5001: LISTENING" -ForegroundColor Green
        $connections = (netstat -an | findstr ":5001" | findstr -v "LISTENING").Count
        Write-Host "  Active Connections: $connections" -ForegroundColor Gray
    } else {
        Write-Host "  Port 5001: NOT LISTENING" -ForegroundColor Red
    }
    Write-Host ""
    
    # Today's Activity
    Write-Host "TODAY'S ACTIVITY" -ForegroundColor Yellow
    $today = Get-Date -Format "yyyyMMdd"
    
    # Count processed orders
    $csvFiles = Get-ChildItem "C:\BarTenderIntegration\Archive" -Filter "*.csv" -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -match $today }
    $orderCount = $csvFiles.Count
    Write-Host "  Orders Processed: $orderCount" -ForegroundColor Green
    
    # Check for errors
    $errorFiles = Get-ChildItem "C:\BarTenderIntegration\ErrorReports" -Filter "*$today*.txt" -ErrorAction SilentlyContinue
    $errorCount = $errorFiles.Count
    $errorColor = if ($errorCount -eq 0) { 'Green' } else { 'Red' }
    Write-Host "  Errors: $errorCount" -ForegroundColor $errorColor
    Write-Host ""
    
    # Recent Orders (Last 5)
    Write-Host "RECENT ORDERS" -ForegroundColor Yellow
    if ($csvFiles.Count -gt 0) {
        $csvFiles | Select-Object -Last 5 | ForEach-Object {
            $orderNum = $_.Name -replace 'order_|_\d{8}_\d{6}\.csv', ''
            $time = $_.LastWriteTime.ToString('HH:mm:ss')
            Write-Host "  $time - Order: $orderNum" -ForegroundColor Gray
        }
    } else {
        Write-Host "  No orders today" -ForegroundColor Gray
    }
    Write-Host ""
    
    # System Health
    Write-Host "SYSTEM HEALTH" -ForegroundColor Yellow
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:5001/health" -TimeoutSec 2
        Write-Host "  API Status: $($health.status)" -ForegroundColor Green
        
        # Get AI status
        $sysStatus = Invoke-RestMethod -Uri "http://localhost:5001/system/status" -TimeoutSec 2
        Write-Host "  Scanner Module: $($sysStatus.modules.scanner)" -ForegroundColor Green
        Write-Host "  AI Module: $($sysStatus.modules.ai)" -ForegroundColor Green
    } catch {
        Write-Host "  API Status: UNREACHABLE" -ForegroundColor Red
    }
    Write-Host ""
    
    # Recent Errors (if any)
    if ($errorCount -gt 0) {
        Write-Host "RECENT ERRORS" -ForegroundColor Red
        $errorFiles | Select-Object -Last 3 | ForEach-Object {
            $content = Get-Content $_.FullName -First 1
            Write-Host "  $($_.Name): $content" -ForegroundColor Red
        }
        Write-Host ""
    }
    
    # Footer
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to exit | Refreshing every 10 seconds..." -ForegroundColor DarkGray
    
    Start-Sleep -Seconds 10
} 