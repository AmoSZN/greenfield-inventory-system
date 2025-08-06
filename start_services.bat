@echo off
echo Starting Greenfield Metal Sales Inventory System...
echo.

echo Starting main inventory system on port 8000...
start "Inventory System" python hybrid_smart_inventory.py

echo Waiting 5 seconds...
timeout /t 5 /nobreak >nul

echo Starting webhook service on port 5001...
start "Webhook Service" python webhook_simple_print.py

echo.
echo Services started!
echo Main system: http://localhost:8000
echo Webhook service: http://localhost:5001
echo.
echo Press any key to exit...
pause >nul
