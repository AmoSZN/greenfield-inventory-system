@echo off
echo Starting Greenfield Inventory System - Production Mode
echo ====================================================

set FLASK_ENV=production
set DEBUG=False

python wsgi.py

pause