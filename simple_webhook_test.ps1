# Simple Webhook Test
Write-Host "🧪 Testing Paradigm Webhook API" -ForegroundColor Cyan

# We already have the token from previous run, but let's get a fresh one
$authResponse = Invoke-RestMethod `
    -Uri "https://greenfieldapi.para-apps.com/api/user/Auth/GetToken" `
    -Method POST `
    -Headers @{"x-api-key" = "nVPsQFBteV&GEd7*8n0%RliVjksag8"} `
    -ContentType "application/json" `
    -Body '{"userName":"web_admin","password":"ChangeMe#123!"}'

$token = $authResponse.data
Write-Host "✅ Got token!" -ForegroundColor Green

# Test 1: Simple webhook with minimal fields
Write-Host "`nTest 1: Minimal webhook" -ForegroundColor Yellow
$simpleWebhook = @{
    address = "https://95891b50740f.ngrok-free.app/webhook/paradigm"
    httpType = "POST"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod `
        -Uri "https://greenfieldapi.para-apps.com/api/Webhook" `
        -Method POST `
        -Headers @{
            "Authorization" = "Bearer $token"
            "x-api-key" = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
        } `
        -ContentType "application/json" `
        -Body $simpleWebhook
    
    Write-Host "✅ Success! Response:" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}

# Test 2: Try different dataType values
Write-Host "`n`nTest 2: Testing different dataType values" -ForegroundColor Yellow
$dataTypes = @("Item", "Items", "Inventory", "Order", "SalesOrder", "PurchaseOrder")

foreach ($type in $dataTypes) {
    Write-Host "   Testing: $type" -ForegroundColor Gray
    
    $testWebhook = @{
        address = "https://95891b50740f.ngrok-free.app/webhook/paradigm"
        dataType = $type
        httpType = "POST"
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod `
            -Uri "https://greenfieldapi.para-apps.com/api/Webhook" `
            -Method POST `
            -Headers @{
                "Authorization" = "Bearer $token"
                "x-api-key" = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
            } `
            -ContentType "application/json" `
            -Body $testWebhook `
            -ErrorAction Stop
        
        Write-Host "   ✅ '$type' worked!" -ForegroundColor Green
        break
    } catch {
        # Silent fail, we're just testing
    }
}

Write-Host "`n📝 Manual Configuration:" -ForegroundColor Cyan
Write-Host "Since the webhook API requires specific dataType values," -ForegroundColor Yellow
Write-Host "you may need to configure webhooks through the Paradigm UI." -ForegroundColor Yellow
Write-Host "`nUse this URL: https://95891b50740f.ngrok-free.app/webhook/paradigm" -ForegroundColor Green