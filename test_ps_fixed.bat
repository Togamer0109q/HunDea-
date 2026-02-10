@echo off
echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║  🧪 QUICK TEST - PlayStation FIXED                  ║
echo ╚══════════════════════════════════════════════════════╝
echo.
echo Testing PlayStation hunter with CORRECT API endpoint...
echo.

python test_playstation_quick.py

echo.
echo ════════════════════════════════════════════════════════
echo.
echo Want to run full ULTIMATE bot? (s/n)
set /p run="→ "

if /i "%run%"=="s" (
    echo.
    python hundea_v3_ultimate.py
)

echo.
pause
