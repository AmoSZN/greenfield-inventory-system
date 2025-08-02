# Test script for Greenfield Label Service
Write-Host "Testing Greenfield Label Service..." -ForegroundColor Green

# Test health endpoint
try {
    $health = Invoke-RestMethod -Uri "http://localhost:5000/health" -Method Get
    Write-Host "✓ Health Check Passed" -ForegroundColor Green
    Write-Host "  Status: $($health.status)" -ForegroundColor White
    Write-Host "  BarTender Installed: $($health.checks.bartender_installed)" -ForegroundColor White
} catch {
    Write-Host "✗ Health Check Failed" -ForegroundColor Red
    Write-Host "  Make sure the webhook service is running!" -ForegroundColor Yellow
    exit
}

# Ask if user wants to send test print
$response = Read-Host "`nSend test print job? (Y/N)"
if ($response -eq 'Y' -or $response -eq 'y') {
    try {
        Write-Host "Sending test print..." -ForegroundColor Yellow
        $result = Invoke-RestMethod -Uri "http://localhost:5000/test-print" -Method Post -ContentType "application/json"
        Write-Host "✓ Test print successful!" -ForegroundColor Green
        Write-Host "  Order Number: $($result.orderNumber)" -ForegroundColor White
        Write-Host "  Labels Printed: $($result.labelsCount)" -ForegroundColor White
    } catch {
        Write-Host "✗ Test print failed" -ForegroundColor Red
        Write-Host "  Error: $_" -ForegroundColor Red
    }
}

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
