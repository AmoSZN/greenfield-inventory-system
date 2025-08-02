# Setup Ngrok for Windows
Write-Host "🌐 Setting up Ngrok for Public Access" -ForegroundColor Cyan
Write-Host "=" * 60

# Check if ngrok exists
if (Test-Path ".\ngrok.exe") {
    Write-Host "✅ Ngrok already installed" -ForegroundColor Green
} else {
    Write-Host "📥 Downloading Ngrok..." -ForegroundColor Yellow
    
    # Download ngrok
    $url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
    $output = "ngrok.zip"
    
    Invoke-WebRequest -Uri $url -OutFile $output
    
    # Extract
    Write-Host "📦 Extracting..." -ForegroundColor Yellow
    Expand-Archive -Path $output -DestinationPath "." -Force
    
    # Clean up
    Remove-Item $output
    
    Write-Host "✅ Ngrok installed!" -ForegroundColor Green
}

Write-Host "`n📝 Instructions:" -ForegroundColor Cyan
Write-Host "1. Run ngrok in a new terminal:"
Write-Host "   .\ngrok http 8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. You'll see output like:"
Write-Host "   Forwarding: https://abc123.ngrok.io -> http://localhost:8000" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Use the https URL for Paradigm webhooks"
Write-Host ""
Write-Host "Press Enter to open a new terminal for ngrok..."
Read-Host

# Start ngrok in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\ngrok http 8000"