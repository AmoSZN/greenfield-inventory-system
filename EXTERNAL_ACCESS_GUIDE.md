# External Access Setup for Paradigm Webhook

## Your Current Setup
- **Public IP**: 172.58.9.227
- **Local Service**: http://localhost:5001/paradigm-webhook
- **Firewall**: ✅ Already configured (port 5001 open)

## Problem
Paradigm (cloud service) needs to reach your local PC, but:
- Your public IP might change (dynamic IP)
- Router needs port forwarding configuration
- Security considerations

## Solution Options

### Option 1: Ngrok (Recommended - Easiest)
Ngrok creates a secure tunnel from the internet to your local service.

#### Install Ngrok:
```powershell
# Download ngrok
Invoke-WebRequest -Uri "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip" -OutFile "ngrok.zip"
Expand-Archive -Path "ngrok.zip" -DestinationPath "."
Remove-Item "ngrok.zip"

# Create account at https://ngrok.com and get auth token
# Then authenticate:
.\ngrok config add-authtoken YOUR_AUTH_TOKEN
```

#### Run Ngrok:
```powershell
# Start ngrok tunnel
.\ngrok http 5001
```

This will give you a URL like: `https://abc123.ngrok.io`

#### Configure Paradigm:
Use the ngrok URL in Paradigm webhook configuration:
- Webhook URL: `https://abc123.ngrok.io/paradigm-webhook`

### Option 2: Port Forwarding (Static IP Required)

If you have a static IP (172.58.9.227):

1. **Router Configuration**:
   - Access router admin (usually 192.168.1.1)
   - Find "Port Forwarding" or "Virtual Server"
   - Add rule:
     - External Port: 5001
     - Internal IP: Your PC's local IP
     - Internal Port: 5001
     - Protocol: TCP

2. **Configure Paradigm**:
   - Webhook URL: `http://172.58.9.227:5001/paradigm-webhook`

### Option 3: Azure/AWS Relay (Production)

For production, consider:
1. Deploy relay service in cloud
2. Local service connects to relay
3. Paradigm webhooks to relay
4. Relay forwards to local service

## Quick Test After Setup

### 1. Test External Access:
```powershell
# From another network or use your phone's data
Invoke-WebRequest -Uri "https://YOUR-NGROK-URL/health"
```

### 2. Configure Paradigm Webhook:
```powershell
# Update configure_paradigm_webhook.py to use external URL
python configure_paradigm_webhook.py
# When prompted for webhook URL, use your ngrok URL
```

### 3. Create Test Order in Paradigm:
- Log into Paradigm
- Create a sales order
- Check local logs for webhook receipt

## Security Considerations

### With Ngrok:
- ✅ HTTPS encryption
- ✅ Random URL (hard to guess)
- ✅ Can add basic auth
- ⚠️ URL changes on restart (paid plan for static)

### With Port Forwarding:
- ⚠️ Exposes service to internet
- ⚠️ Should add authentication
- ⚠️ Consider VPN instead

## Recommended Setup Script

Create `start_with_ngrok.ps1`:
```powershell
Write-Host "Starting Greenfield Label Service with Ngrok..." -ForegroundColor Cyan

# Start webhook service
Write-Host "Starting webhook service..." -ForegroundColor Yellow
Start-Process python -ArgumentList "webhook_simple_print.py" -WindowStyle Minimized

# Wait for service to start
Start-Sleep -Seconds 5

# Start ngrok
Write-Host "Starting ngrok tunnel..." -ForegroundColor Yellow
Start-Process .\ngrok -ArgumentList "http 5001"

Write-Host "`nSetup complete!" -ForegroundColor Green
Write-Host "1. Copy the ngrok URL from the ngrok window" -ForegroundColor White
Write-Host "2. Configure this URL in Paradigm webhooks" -ForegroundColor White
Write-Host "3. Monitor logs: Get-Content 'C:\BarTenderIntegration\Logs\webhook_$(Get-Date -Format 'yyyyMMdd').log' -Wait" -ForegroundColor White
```

## Next Steps
1. Choose your access method (ngrok recommended)
2. Set up the tunnel/forwarding
3. Update Paradigm webhook URL
4. Test with real order 