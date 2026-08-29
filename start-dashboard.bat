@echo off
title Razorpay RiskGuard - Dashboard
echo Starting Razorpay RiskGuard Dashboard...
echo.
echo  Dashboard: http://localhost:3000
echo.
cd /d "%~dp0frontend"
npm run dev
pause
