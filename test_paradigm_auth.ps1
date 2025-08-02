# Test Paradigm Authentication
Write-Host "Testing Paradigm Authentication..." -ForegroundColor Cyan

# Method 1: Using curl
Write-Host "`nMethod 1: Using curl" -ForegroundColor Yellow
$curlCommand = @'
curl -X POST "https://greenfieldapi.para-apps.com/api/Authenticate" -H "x-api-key: nVPsQFBteV&GEd7*8n0%RliVjksag8" -H "Content-Type: application/json" -d "{\"userName\":\"web_admin\",\"password\":\"ChangeMe#123!\"}"
'@
Write-Host $curlCommand -ForegroundColor Gray
Write-Host "`nCopy and paste the above curl command`n"

# Method 2: Using Invoke-WebRequest
Write-Host "`nMethod 2: Using Invoke-WebRequest" -ForegroundColor Yellow
try {
    $headers = @{
        "x-api-key" = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
        "Content-Type" = "application/json"
    }
    
    $body = @{
        userName = "web_admin"
        password = "ChangeMe#123!"
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "https://greenfieldapi.para-apps.com/api/Authenticate" `
        -Method POST `
        -Headers $headers `
        -Body $body `
        -UseBasicParsing
    
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor Gray
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "Status: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
}

# Method 3: Simple webhook test
Write-Host "`n`nDirect Webhook Configuration (if you have a token):" -ForegroundColor Yellow
Write-Host @'
# If you get a token from the Paradigm UI or another method, use:
$token = "YOUR_TOKEN_HERE"

# Then create webhook:
curl -X POST "https://greenfieldapi.para-apps.com/api/Webhook" `
  -H "Authorization: Bearer $token" `
  -H "x-api-key: nVPsQFBteV&GEd7*8n0%RliVjksag8" `
  -H "Content-Type: application/json" `
  -d "{\"address\":\"https://95891b50740f.ngrok-free.app/webhook/paradigm\",\"dataOperation\":\"UPDATE\",\"dataType\":\"INVENTORY\",\"httpType\":\"POST\"}"
'@ -ForegroundColor Gray