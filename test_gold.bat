@echo off
REM ╔══════════════════════════════════════════════════════╗
REM ║  🎁 TEST GAMERPOWER - FREE WEEKENDS & GIVEAWAYS     ║
REM ╚══════════════════════════════════════════════════════╝

echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║  🎁 GAMERPOWER API TEST                              ║
echo ║  Free Weekends + Giveaways Hunter                    ║
echo ╚══════════════════════════════════════════════════════╝
echo.

echo Testing GamerPower API (100%% FREE, no key needed!)...
echo.

python modules/gamerpower_hunter.py

echo.
echo ════════════════════════════════════════════════════════
echo.
echo ¿Quieres ver la documentación de APIs encontradas? (s/n)
set /p docs="→ "

if /i "%docs%"=="s" (
    echo.
    type GOLD_APIS_FOUND.md
)

echo.
pause
