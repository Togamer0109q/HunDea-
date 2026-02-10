@echo off
REM ╔═══════════════════════════════════════════════════════════╗
REM ║  🎮 PLATPRICES SETUP - ONE CLICK                         ║
REM ╚═══════════════════════════════════════════════════════════╝

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║  🎮 PLATPRICES API KEY SETUP                             ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Step 1: Configure
echo 1️⃣  Configurando API key...
python setup_platprices.py
if errorlevel 1 (
    echo ❌ Setup failed
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════
echo.

REM Step 2: Test
echo 2️⃣  Testing PlayStation hunter...
python test_playstation.py

echo.
echo ═══════════════════════════════════════════════════════════
echo.

REM Step 3: Ask to run full bot
echo 3️⃣  ¿Ejecutar bot completo? (s/n)
set /p run_bot="→ "

if /i "%run_bot%"=="s" (
    echo.
    echo 🚀 Ejecutando bot completo...
    python hundea_v3.py
) else (
    echo.
    echo ✅ Setup completo!
    echo.
    echo Para ejecutar el bot después:
    echo    python hundea_v3.py
)

echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
