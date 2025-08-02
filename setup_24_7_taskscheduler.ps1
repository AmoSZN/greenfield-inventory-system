# Setup 24/7 Operation using Windows Task Scheduler
Write-Host "🔧 Setting up 24/7 Inventory System" -ForegroundColor Cyan
Write-Host "=" * 60

$currentDir = Get-Location
$pythonExe = (Get-Command python).Source
$scriptPath = Join-Path $currentDir "inventory_system_24_7.py"

Write-Host "📁 Directory: $currentDir" -ForegroundColor Gray
Write-Host "🐍 Python: $pythonExe" -ForegroundColor Gray
Write-Host "📜 Script: $scriptPath" -ForegroundColor Gray

# Create startup batch file
$batchFile = Join-Path $currentDir "start_inventory_system.bat"
$batchContent = @"
@echo off
cd /d "$currentDir"
echo Starting Greenfield Inventory System...
echo Access at: http://localhost:8000
"$pythonExe" "$scriptPath"
pause
"@

Write-Host "`n1️⃣ Creating startup script..." -ForegroundColor Yellow
$batchContent | Out-File -FilePath $batchFile -Encoding ASCII
Write-Host "✅ Created: $batchFile" -ForegroundColor Green

# Create scheduled task
Write-Host "`n2️⃣ Creating scheduled task..." -ForegroundColor Yellow

$taskName = "GreenfieldInventorySystem"
$description = "AI-powered inventory management system - 24/7 operation"

# Remove existing task if it exists
try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
} catch {}

# Create new task
$action = New-ScheduledTaskAction -Execute $batchFile
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

$task = New-ScheduledTask -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description $description

try {
    Register-ScheduledTask -TaskName $taskName -InputObject $task
    Write-Host "✅ Scheduled task created successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create scheduled task: $_" -ForegroundColor Red
}

# Create desktop shortcut
Write-Host "`n3️⃣ Creating desktop shortcut..." -ForegroundColor Yellow

$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "Greenfield Inventory System.lnk"

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $batchFile
$shortcut.WorkingDirectory = $currentDir
$shortcut.Description = "Greenfield Inventory System - AI-powered inventory management"
$shortcut.IconLocation = "$pythonExe,0"
$shortcut.Save()

Write-Host "✅ Desktop shortcut created!" -ForegroundColor Green

# Create startup folder shortcut for auto-start
Write-Host "`n4️⃣ Setting up auto-start..." -ForegroundColor Yellow

$startupPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$startupShortcut = Join-Path $startupPath "Greenfield Inventory System.lnk"

$startupLink = $shell.CreateShortcut($startupShortcut)
$startupLink.TargetPath = $batchFile
$startupLink.WorkingDirectory = $currentDir
$startupLink.Description = "Auto-start Greenfield Inventory System"
$startupLink.Save()

Write-Host "✅ Auto-start configured!" -ForegroundColor Green

Write-Host "`n" + ("=" * 60)
Write-Host "🎉 24/7 SETUP COMPLETE!" -ForegroundColor Green
Write-Host "`n📋 What was configured:" -ForegroundColor Cyan
Write-Host "   ✅ Startup script: start_inventory_system.bat"
Write-Host "   ✅ Scheduled task: GreenfieldInventorySystem"
Write-Host "   ✅ Desktop shortcut created"
Write-Host "   ✅ Auto-start on Windows startup"

Write-Host "`n🌐 Access URLs:" -ForegroundColor Cyan
Write-Host "   Local: http://localhost:8000"
Write-Host "   Network: http://192.168.12.78:8000"

Write-Host "`n🔧 Management:" -ForegroundColor Cyan
Write-Host "   Start manually: Double-click desktop shortcut"
Write-Host "   Auto-starts: On Windows boot"
Write-Host "   Stop: Close the command window"

Write-Host "`n🚀 Starting system now..." -ForegroundColor Yellow
Start-Process $batchFile