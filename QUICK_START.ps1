# Greenfield Label Service - Quick Start Script
# This script helps you navigate to the correct directory and run verification

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "GREENFIELD LABEL SERVICE - QUICK START" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to the project directory
$projectPath = "C:\Users\mattm\OneDrive\Greenfield Metal Sales\Barcode Scanner"
Write-Host "Navigating to project directory..." -ForegroundColor Yellow
Set-Location $projectPath
Write-Host "✓ Current directory: $pwd" -ForegroundColor Green
Write-Host ""

# Display your network information
Write-Host "NETWORK INFORMATION" -ForegroundColor Yellow
Write-Host "Public IP: 172.58.9.227" -ForegroundColor Green
$localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -like "192.168.*"}).IPAddress | Select-Object -First 1
Write-Host "Local IP: $localIP" -ForegroundColor Green
Write-Host "Webhook URL: http://${localIP}:5001/paradigm-webhook" -ForegroundColor Green
Write-Host ""

# Check if webhook service is running
Write-Host "CHECKING SERVICES" -ForegroundColor Yellow
$pythonProcesses = Get-Process python* -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "⚠️  Python processes running. Stopping them..." -ForegroundColor Yellow
    $pythonProcesses | Stop-Process -Force
    Start-Sleep -Seconds 2
}
Write-Host "✓ Ready to start fresh" -ForegroundColor Green
Write-Host ""

# Menu
Write-Host "WHAT WOULD YOU LIKE TO DO?" -ForegroundColor Cyan
Write-Host "1. Run verification test" -ForegroundColor White
Write-Host "2. Configure Paradigm webhook" -ForegroundColor White
Write-Host "3. Start webhook service (simple mode)" -ForegroundColor White
Write-Host "4. Start integrated system (with AI)" -ForegroundColor White
Write-Host "5. Test print" -ForegroundColor White
Write-Host "6. Deploy as Windows service" -ForegroundColor White
Write-Host "7. View logs" -ForegroundColor White
Write-Host "8. Set up ngrok (external access)" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1-8)"

switch ($choice) {
    "1" {
        Write-Host "`nRunning verification test..." -ForegroundColor Yellow
        python verify_paradigm_integration.py
    }
    "2" {
        Write-Host "`nConfiguring Paradigm webhook..." -ForegroundColor Yellow
        python configure_paradigm_webhook.py
    }
    "3" {
        Write-Host "`nStarting webhook service (simple mode)..." -ForegroundColor Yellow
        python webhook_simple_print.py
    }
    "4" {
        Write-Host "`nStarting integrated system (with AI)..." -ForegroundColor Yellow
        python main_app.py
    }
    "5" {
        Write-Host "`nTesting print..." -ForegroundColor Yellow
        try {
            $result = Invoke-RestMethod -Uri "http://localhost:5001/test-print" -TimeoutSec 10
            Write-Host "✓ Print successful!" -ForegroundColor Green
            $result | ConvertTo-Json
        } catch {
            Write-Host "✗ Print failed - is the service running?" -ForegroundColor Red
        }
    }
    "6" {
        Write-Host "`nTo deploy as Windows service:" -ForegroundColor Yellow
        Write-Host "1. Open PowerShell as Administrator" -ForegroundColor White
        Write-Host "2. Navigate to: $projectPath" -ForegroundColor White
        Write-Host "3. Run: .\install_as_service.bat" -ForegroundColor White
        Write-Host ""
        Write-Host "Press Enter to continue..."
        Read-Host
    }
    "7" {
        Write-Host "`nViewing recent logs..." -ForegroundColor Yellow
        $today = Get-Date -Format "yyyyMMdd"
        $logFile = "C:\BarTenderIntegration\Logs\webhook_$today.log"
        if (Test-Path $logFile) {
            Get-Content $logFile -Tail 20
        } else {
            Write-Host "No logs found for today" -ForegroundColor Yellow
        }
    }
    "8" {
        Write-Host "`nSetting up ngrok for external access..." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "This will let Paradigm send orders to your computer." -ForegroundColor White
        Write-Host ""
        
        # Check if ngrok exists
        if (Test-Path ".\ngrok.exe") {
            Write-Host "✓ Ngrok already installed" -ForegroundColor Green
        } else {
            Write-Host "Downloading ngrok..." -ForegroundColor Yellow
            Invoke-WebRequest -Uri "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip" -OutFile "ngrok.zip"
            Expand-Archive -Path "ngrok.zip" -DestinationPath "." -Force
            Remove-Item "ngrok.zip"
            Write-Host "✓ Ngrok downloaded" -ForegroundColor Green
        }
        
        Write-Host ""
        Write-Host "Starting ngrok tunnel..." -ForegroundColor Yellow
        Write-Host "A new window will open showing your ngrok URL" -ForegroundColor White
        Write-Host ""
        Write-Host "IMPORTANT: Copy the URL that looks like:" -ForegroundColor Yellow
        Write-Host "  https://abc123.ngrok.io" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Press Enter to start ngrok..."
        Read-Host
        
        Start-Process .\ngrok.exe -ArgumentList "http 5001"
        
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Yellow
        Write-Host "1. Copy the ngrok URL from the new window" -ForegroundColor White
        Write-Host "2. Add '/paradigm-webhook' to the end" -ForegroundColor White
        Write-Host "3. Use this full URL in Paradigm webhook settings" -ForegroundColor White
    }
    default {
        Write-Host "Invalid choice!" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Press Enter to exit..."
Read-Host 