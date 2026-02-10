@echo off
REM ╔═══════════════════════════════════════════════════════════╗
REM ║  🧪 TEST ALL HUNTERS - Quick Verification                ║
REM ╚═══════════════════════════════════════════════════════════╝

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║  🧪 TESTING ALL HUNTERS                                  ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Test all hunters
python test_all_hunters.py

echo.
echo ═══════════════════════════════════════════════════════════
echo.

REM Ask if want to run full bot
echo ¿Ejecutar bot completo ahora? (s/n)
set /p run_bot="→ "

if /i "%run_bot%"=="s" (
    echo.
    echo 🚀 Ejecutando bot completo...
    echo.
    python hundea_v3.py
) else (
    echo.
    echo ✅ Tests completados!
    echo.
    echo Para ejecutar el bot después:
    echo    python hundea_v3.py
)

echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
