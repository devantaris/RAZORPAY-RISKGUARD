@echo off
title Razorpay RiskGuard - Backend API
echo Starting Razorpay RiskGuard Backend...
echo.
echo  API Docs:  http://localhost:8000/docs
echo  Health:    http://localhost:8000/v1/health
echo.
cd /d "%~dp0backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info
pause
