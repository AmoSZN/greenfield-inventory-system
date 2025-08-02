# Greenfield Inventory AI - External Access Setup
# Run this as Administrator

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "GREENFIELD INVENTORY AI - EXTERNAL ACCESS SETUP" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Get current network info
$localIP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Ethernet*", "Wi-Fi*" | Where-Object {$_.IPAddress -notlike "169.254.*"} | Select-Object -First 1).IPAddress
$publicIP = (Invoke-RestMethod -Uri "https://api.ipify.org?format=text" -ErrorAction SilentlyContinue)

Write-Host "📊 Current Network Configuration:" -ForegroundColor Yellow
Write-Host "   Local IP: $localIP"
Write-Host "   Public IP: $publicIP"
Write-Host ""

Write-Host "Choose your external access method:" -ForegroundColor Yellow
Write-Host "1. Port Forwarding (Recommended for static IP)"
Write-Host "2. Ngrok Tunnel (Easy - no router config needed)"
Write-Host "3. Cloud Deployment (Professional solution)"
Write-Host ""

$choice = Read-Host "Enter your choice (1-3)"

switch ($choice) {
    "1" {
        Write-Host "`n📋 PORT FORWARDING SETUP" -ForegroundColor Green
        Write-Host "================================"
        Write-Host ""
        Write-Host "1. Log into your router admin panel"
        Write-Host "   Common addresses: 192.168.1.1 or 192.168.0.1"
        Write-Host ""
        Write-Host "2. Find 'Port Forwarding' or 'Virtual Server' section"
        Write-Host ""
        Write-Host "3. Add new rule:"
        Write-Host "   - External Port: 8000"
        Write-Host "   - Internal IP: $localIP"
        Write-Host "   - Internal Port: 8000"
        Write-Host "   - Protocol: TCP"
        Write-Host ""
        Write-Host "4. Save and apply changes"
        Write-Host ""
        Write-Host "5. Access your system at: http://${publicIP}:8000"
        Write-Host ""
        
        # Configure Windows Firewall
        Write-Host "Configuring Windows Firewall..." -ForegroundColor Yellow
        New-NetFirewallRule -DisplayName "Greenfield Inventory AI" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue
        Write-Host "✅ Firewall rule created" -ForegroundColor Green
    }
    
    "2" {
        Write-Host "`n📋 NGROK SETUP" -ForegroundColor Green
        Write-Host "================================"
        Write-Host ""
        
        # Check if ngrok exists
        if (!(Test-Path ".\ngrok.exe")) {
            Write-Host "Downloading ngrok..." -ForegroundColor Yellow
            Invoke-WebRequest -Uri "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip" -OutFile "ngrok.zip"
            Expand-Archive -Path "ngrok.zip" -DestinationPath "." -Force
            Remove-Item "ngrok.zip"
            Write-Host "✅ Ngrok downloaded" -ForegroundColor Green
        }
        
        Write-Host ""
        Write-Host "Starting ngrok tunnel..." -ForegroundColor Yellow
        Write-Host "Keep this window open!" -ForegroundColor Red
        Write-Host ""
        
        # Create ngrok config
        @"
version: "2"
authtoken: YOUR_AUTH_TOKEN_HERE
tunnels:
  inventory:
    proto: http
    addr: 8000
    inspect: false
"@ | Out-File -FilePath "ngrok.yml" -Encoding UTF8
        
        Write-Host "To use ngrok:" -ForegroundColor Yellow
        Write-Host "1. Sign up at https://ngrok.com (free)"
        Write-Host "2. Get your auth token"
        Write-Host "3. Run: .\ngrok config add-authtoken YOUR_TOKEN"
        Write-Host "4. Run: .\ngrok http 8000"
        Write-Host ""
        Write-Host "Your public URL will be shown (e.g., https://abc123.ngrok.io)"
    }
    
    "3" {
        Write-Host "`n📋 CLOUD DEPLOYMENT GUIDE" -ForegroundColor Green
        Write-Host "================================"
        Write-Host ""
        Write-Host "Recommended: Azure App Service" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. Install Azure CLI:"
        Write-Host "   winget install Microsoft.AzureCLI"
        Write-Host ""
        Write-Host "2. Login to Azure:"
        Write-Host "   az login"
        Write-Host ""
        Write-Host "3. Create deployment package:"
        Write-Host "   See CLOUD_DEPLOY.md for details"
        Write-Host ""
        Write-Host "Benefits:" -ForegroundColor Green
        Write-Host "   ✅ Always available"
        Write-Host "   ✅ Auto-scaling"
        Write-Host "   ✅ Professional URL"
        Write-Host "   ✅ Built-in security"
    }
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Need help? Check EXTERNAL_ACCESS_GUIDE.md" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan