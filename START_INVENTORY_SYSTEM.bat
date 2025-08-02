@echo off
title Greenfield Inventory System - 24/7
cd /d "C:\Users\mattm\OneDrive\Greenfield Metal Sales\Barcode Scanner"
echo.
echo ============================================================
echo 🏭 GREENFIELD INVENTORY SYSTEM - STARTING...
echo ============================================================
echo 🌐 Will be available at: http://localhost:8000
echo 📱 Network access at: http://192.168.12.78:8000
echo ============================================================
echo.
"C:\Python313\python.exe" "C:\Users\mattm\OneDrive\Greenfield Metal Sales\Barcode Scanner\inventory_system_24_7.py"
echo.
echo ============================================================
echo 🛑 SYSTEM STOPPED
echo ============================================================
pause
