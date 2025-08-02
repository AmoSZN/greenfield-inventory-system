# Paradigm Webhook Configuration Script
# Copy and paste these commands one by one

Write-Host "🔧 Configuring Paradigm Webhooks" -ForegroundColor Cyan
Write-Host "=" * 60

# Step 1: Authenticate with Paradigm
Write-Host "`n1️⃣ Authenticating with Paradigm..." -ForegroundColor Yellow

$authBody = @{
    userName = "web_admin"
    password = "ChangeMe#123!"
} | ConvertTo-Json

$authResponse = Invoke-RestMethod -Uri "https://greenfieldapi.para-apps.com/api/Authenticate" `
    -Method POST `
    -Headers @{"x-api-key" = "nVPsQFBteV&GEd7*8n0%RliVjksag8"} `
    -ContentType "application/json" `
    -Body $authBody

if ($authResponse.data.token) {
    $token = $authResponse.data.token
    Write-Host "✅ Authentication successful!" -ForegroundColor Green
    Write-Host "Token: $($token.Substring(0,20))..." -ForegroundColor Gray
} else {
    Write-Host "❌ Authentication failed!" -ForegroundColor Red
    exit
}

# Step 2: Create Inventory Update Webhook
Write-Host "`n2️⃣ Creating Inventory Update Webhook..." -ForegroundColor Yellow

$webhookBody1 = @{
    address = "https://95891b50740f.ngrok-free.app/webhook/paradigm"
    dataOperation = "UPDATE"
    dataType = "INVENTORY"
    httpType = "POST"
} | ConvertTo-Json

try {
    $webhook1 = Invoke-RestMethod -Uri "https://greenfieldapi.para-apps.com/api/Webhook" `
        -Method POST `
        -Headers @{
            "Authorization" = "Bearer $token"
            "x-api-key" = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
        } `
        -ContentType "application/json" `
        -Body $webhookBody1
    
    Write-Host "✅ Inventory webhook created!" -ForegroundColor Green
} catch {
    Write-Host "❌ Error creating inventory webhook: $_" -ForegroundColor Red
}

# Step 3: Create Sales Order Webhook
Write-Host "`n3️⃣ Creating Sales Order Webhook..." -ForegroundColor Yellow

$webhookBody2 = @{
    address = "https://95891b50740f.ngrok-free.app/webhook/paradigm"
    dataOperation = "CREATE"
    dataType = "SALES_ORDER"
    httpType = "POST"
} | ConvertTo-Json

try {
    $webhook2 = Invoke-RestMethod -Uri "https://greenfieldapi.para-apps.com/api/Webhook" `
        -Method POST `
        -Headers @{
            "Authorization" = "Bearer $token"
            "x-api-key" = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
        } `
        -ContentType "application/json" `
        -Body $webhookBody2
    
    Write-Host "✅ Sales order webhook created!" -ForegroundColor Green
} catch {
    Write-Host "❌ Error creating sales webhook: $_" -ForegroundColor Red
}

# Step 4: Create Purchase Order Webhook
Write-Host "`n4️⃣ Creating Purchase Order Webhook..." -ForegroundColor Yellow

$webhookBody3 = @{
    address = "https://95891b50740f.ngrok-free.app/webhook/paradigm"
    dataOperation = "CREATE"
    dataType = "PURCHASE_ORDER"
    httpType = "POST"
} | ConvertTo-Json

try {
    $webhook3 = Invoke-RestMethod -Uri "https://greenfieldapi.para-apps.com/api/Webhook" `
        -Method POST `
        -Headers @{
            "Authorization" = "Bearer $token"
            "x-api-key" = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
        } `
        -ContentType "application/json" `
        -Body $webhookBody3
    
    Write-Host "✅ Purchase order webhook created!" -ForegroundColor Green
} catch {
    Write-Host "❌ Error creating purchase webhook: $_" -ForegroundColor Red
}

# Step 5: Create Stock Adjustment Webhook
Write-Host "`n5️⃣ Creating Stock Adjustment Webhook..." -ForegroundColor Yellow

$webhookBody4 = @{
    address = "https://95891b50740f.ngrok-free.app/webhook/paradigm"
    dataOperation = "UPDATE"
    dataType = "STOCK_ADJUSTMENT"
    httpType = "POST"
} | ConvertTo-Json

try {
    $webhook4 = Invoke-RestMethod -Uri "https://greenfieldapi.para-apps.com/api/Webhook" `
        -Method POST `
        -Headers @{
            "Authorization" = "Bearer $token"
            "x-api-key" = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
        } `
        -ContentType "application/json" `
        -Body $webhookBody4
    
    Write-Host "✅ Stock adjustment webhook created!" -ForegroundColor Green
} catch {
    Write-Host "❌ Error creating adjustment webhook: $_" -ForegroundColor Red
}

Write-Host "`n" + ("=" * 60)
Write-Host "📊 WEBHOOK CONFIGURATION COMPLETE!" -ForegroundColor Green
Write-Host "`nYour webhook URL: https://95891b50740f.ngrok-free.app/webhook/paradigm" -ForegroundColor Cyan
Write-Host "`n📝 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Make a change in Paradigm (update inventory)"
Write-Host "2. Watch the ngrok window for incoming webhooks"
Write-Host "3. Check http://localhost:8000 for updates"