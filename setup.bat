@echo off
echo ========================================
echo   HunDeaBot v3.0 - Setup Installer
echo ========================================
echo.

:: Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.8+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Python found: 
python --version
echo.

:: Install dependencies
echo [2/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo.

:: Create config from example
if not exist config.json (
    echo [3/4] Creating config.json from example...
    copy config_v3.example.json config.json
    echo [!] Please edit config.json with your webhooks and API keys
) else (
    echo [3/4] config.json already exists, skipping...
)
echo.

:: Create cache file if missing
if not exist cache.json (
    echo [4/4] Creating cache.json...
    echo {} > cache.json
) else (
    echo [4/4] cache.json already exists
)
echo.

echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Edit config.json with your Discord webhooks
echo   2. (Optional) Add RAWG API key for better scoring
echo   3. Run: python hundea_v3.py
echo.
echo For help, see README.md
pause
