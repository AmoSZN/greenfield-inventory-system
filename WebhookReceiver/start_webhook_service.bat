@echo off
title Greenfield Metal Sales - Label Print Service
echo ============================================================
echo GREENFIELD METAL SALES - LABEL PRINT SERVICE
echo ============================================================
echo.
echo Starting webhook receiver service...
echo.
cd /d C:\BarTenderIntegration\WebhookReceiver
python webhook_receiver.py
pause
