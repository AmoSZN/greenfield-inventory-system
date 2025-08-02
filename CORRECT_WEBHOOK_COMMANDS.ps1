# CORRECT Paradigm Webhook Configuration
Write-Host "🔧 Setting up Paradigm Webhooks with CORRECT endpoints" -ForegroundColor Cyan
Write-Host "=" * 60

# Step 1: Authenticate using the CORRECT endpoint
Write-Host "`n1️⃣ Authenticating..." -ForegroundColor Yellow

$authBody = @{
    userName = "web_admin"
    password = "ChangeMe#123!"
} | ConvertTo-Json

try {
    $authResponse = Invoke-RestMethod `
        -Uri "https://greenfieldapi.para-apps.com/api/user/Auth/GetToken" `
        -Method POST `
        -Headers @{"x-api-key" = "nVPsQFBteV&GEd7*8n0%RliVjksag8"} `
        -ContentType "application/json" `
        -Body $authBody
    
    if ($authResponse.isLoginValid) {
        $token = $authResponse.data
        Write-Host "✅ Authentication successful!" -ForegroundColor Green
        Write-Host "Token received: $($token.Substring(0,20))..." -ForegroundColor Gray
    } else {
        Write-Host "❌ Login invalid!" -ForegroundColor Red
        exit
    }
} catch {
    Write-Host "❌ Auth error: $_" -ForegroundColor Red
    exit
}

# Step 2: Create webhooks
Write-Host "`n2️⃣ Creating webhooks..." -ForegroundColor Yellow

# Webhook configurations
$webhooks = @(
    @{
        name = "Inventory Updates"
        body = @{
            address = "https://95891b50740f.ngrok-free.app/webhook/paradigm"
            dataOperation = "UPDATE"
            dataType = "INVENTORY"
            httpType = "POST"
        }
    },
    @{
        name = "Sales Orders"
        body = @{
            address = "https://95891b50740f.ngrok-free.app/webhook/paradigm"
            dataOperation = "CREATE"
            dataType = "SALES_ORDER"
            httpType = "POST"
        }
    },
    @{
        name = "Purchase Orders"
        body = @{
            address = "https://95891b50740f.ngrok-free.app/webhook/paradigm"
            dataOperation = "CREATE"
            dataType = "PURCHASE_ORDER"
            httpType = "POST"
        }
    }
)

$headers = @{
    "Authorization" = "Bearer $token"
    "x-api-key" = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
    "Content-Type" = "application/json"
}

foreach ($webhook in $webhooks) {
    Write-Host "   Creating: $($webhook.name)" -ForegroundColor Yellow
    
    try {
        $response = Invoke-RestMethod `
            -Uri "https://greenfieldapi.para-apps.com/api/Webhook" `
            -Method POST `
            -Headers $headers `
            -Body ($webhook.body | ConvertTo-Json)
        
        Write-Host "   ✅ $($webhook.name) created!" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ Error: $_" -ForegroundColor Red
    }
}

Write-Host "`n" + ("=" * 60)
Write-Host "📊 SETUP COMPLETE!" -ForegroundColor Green
Write-Host "`nWebhook URL: https://95891b50740f.ngrok-free.app/webhook/paradigm" -ForegroundColor Cyan
Write-Host "`n📝 Test by:" -ForegroundColor Yellow
Write-Host "1. Making a change in Paradigm"
Write-Host "2. Watching the ngrok window"
Write-Host "3. Checking http://localhost:8000"