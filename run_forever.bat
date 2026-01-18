@echo off
title Bybit Trading Bot 24/7
color 0A

:loop
cls
echo ====================================================
echo        BYBIT VOLUME BOT - 24/7 WATCHDOG
echo ====================================================
echo Start time: %time%
echo.
echo Starting main.py...
echo.

python main.py

echo.
echo ====================================================
echo [WARNING] Bot stopped/crashed at %time%
echo Restarting in 5 seconds...
echo Press Ctrl+C to stop permanently.
echo ====================================================
timeout /t 5 >nul
goto loop
