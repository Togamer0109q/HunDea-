@echo off
REM ╔═══════════════════════════════════════════════════════════╗
REM ║  🚀 HUNDEABOT ULTIMATE - Quick Launcher                  ║
REM ╚═══════════════════════════════════════════════════════════╝

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║  🚀 HUNDEABOT V3.0 ULTIMATE                              ║
echo ║  All Hunters Edition                                     ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

echo ¿Qué quieres ejecutar?
echo.
echo 1. 🧪 Test ALL hunters (recomendado)
echo 2. 🚀 ULTIMATE bot (todos los hunters)
echo 3. 💻 Bot v3.0 standard
echo.

set /p choice="→ Elige (1-3): "

if "%choice%"=="1" goto test
if "%choice%"=="2" goto ultimate
if "%choice%"=="3" goto standard
goto error

:test
echo.
echo 🧪 Testing ALL hunters...
echo.
python test_all_hunters.py
goto end

:ultimate
echo.
echo 🚀 Ejecutando ULTIMATE bot...
echo.
python hundea_v3_ultimate.py
goto end

:standard
echo.
echo 💻 Ejecutando bot standard...
echo.
python hundea_v3.py
goto end

:error
echo.
echo ❌ Opción inválida
goto end

:end
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
