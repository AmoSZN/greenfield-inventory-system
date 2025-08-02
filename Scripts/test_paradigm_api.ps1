# Paradigm API Test Script for Greenfield Metal Sales
param(
    [string]$OrderNumber = "",
    [switch]$ListEndpoints,
    [switch]$TestConnection
)

# Configuration
$API_URL = "https://greenfieldapi.para-apps.com"
$API_KEY = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
$USERNAME = "mattamundson@greenfieldmetalsales.com"
$PASSWORD = "Morrison216!"

# Create authentication headers
$credentials = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${USERNAME}:${PASSWORD}"))
$headers = @{
    "Authorization" = "Basic $credentials"
    "X-API-Key" = $API_KEY
    "Content-Type" = "application/json"
}

function Test-APIConnection {
    Write-Host "Testing Paradigm API Connection..." -ForegroundColor Green
    
    try {
        $response = Invoke-RestMethod -Uri "$API_URL/api" -Headers $headers -Method Get -TimeoutSec 10
        Write-Host "✓ API connection successful!" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "✗ API connection failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Get-APIEndpoints {
    Write-Host "Discovering available API endpoints..." -ForegroundColor Yellow
    
    $endpoints = @(
        "/api",
        "/api/orders",
        "/api/sales-orders", 
        "/api/customers",
        "/api/products",
        "/api/inventory"
    )
    
    foreach ($endpoint in $endpoints) {
        try {
            $url = "$API_URL$endpoint"
            $response = Invoke-WebRequest -Uri $url -Headers $headers -Method Get -TimeoutSec 5 -UseBasicParsing
            Write-Host "✓ $endpoint - Available (Status: $($response.StatusCode))" -ForegroundColor Green
        } catch {
            $statusCode = $_.Exception.Response.StatusCode.value__
            if ($statusCode -eq 401) {
                Write-Host "⚠ $endpoint - Authentication required" -ForegroundColor Yellow
            } elseif ($statusCode -eq 404) {
                Write-Host "✗ $endpoint - Not found" -ForegroundColor Red
            } else {
                Write-Host "? $endpoint - Status: $statusCode" -ForegroundColor Gray
            }
        }
    }
}

function Get-OrderData {
    param([string]$OrderNum)
    
    if ([string]::IsNullOrEmpty($OrderNum)) {
        Write-Host "Please provide an order number" -ForegroundColor Red
        return
    }
    
    Write-Host "Fetching order: $OrderNum" -ForegroundColor Yellow
    
    # Try different order endpoints
    $orderEndpoints = @(
        "/api/orders/$OrderNum",
        "/api/sales-orders/$OrderNum",
        "/api/order?number=$OrderNum",
        "/orders/$OrderNum"
    )
    
    foreach ($endpoint in $orderEndpoints) {
        try {
            $url = "$API_URL$endpoint"
            Write-Host "Trying: $endpoint" -ForegroundColor Gray
            
            $response = Invoke-RestMethod -Uri $url -Headers $headers -Method Get -TimeoutSec 10
            
            Write-Host "✓ Found order data at: $endpoint" -ForegroundColor Green
            Write-Host "Raw API Response:" -ForegroundColor Cyan
            $response | ConvertTo-Json -Depth 5
            
            # Save to file for analysis
            $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
            $filename = "order_${OrderNum}_${timestamp}.json"
            $filepath = "C:\BarTenderIntegration\Data\OrderData\$filename"
            
            $response | ConvertTo-Json -Depth 10 | Out-File -FilePath $filepath -Encoding UTF8
            Write-Host "`nSaved to: $filepath" -ForegroundColor Green
            
            return $response
            
        } catch {
            Write-Host "✗ $endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    Write-Host "❌ Order $OrderNum not found in any endpoint" -ForegroundColor Red
}

# Main execution
if ($TestConnection) {
    Test-APIConnection
}

if ($ListEndpoints) {
    Get-APIEndpoints
}

if ($OrderNumber) {
    if (Test-APIConnection) {
        Get-OrderData -OrderNum $OrderNumber
    }
}

if (-not $TestConnection -and -not $ListEndpoints -and -not $OrderNumber) {
    Write-Host "Paradigm API Test Script" -ForegroundColor Green
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\test_paradigm_api.ps1 -TestConnection" -ForegroundColor White
    Write-Host "  .\test_paradigm_api.ps1 -ListEndpoints" -ForegroundColor White
    Write-Host "  .\test_paradigm_api.ps1 -OrderNumber 'SO-2024-001'" -ForegroundColor White
}
