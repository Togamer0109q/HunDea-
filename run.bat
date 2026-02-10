@echo off
title HunDeaBot v3.0
echo ========================================
echo   Starting HunDeaBot v3.0
echo ========================================
echo.

:: Check if config exists
if not exist config.json (
    echo [ERROR] config.json not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

:: Run the bot
echo [INFO] Launching bot...
echo.
python hundea_v3.py

:: Keep window open if error
if errorlevel 1 (
    echo.
    echo [ERROR] Bot crashed or stopped with errors
    pause
)
