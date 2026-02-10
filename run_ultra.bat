@echo off
REM ╔═══════════════════════════════════════════════════════════╗
REM ║  🚀 HUNDEABOT V3 ULTRA - MAXIMUM POWER LAUNCHER          ║
REM ╚═══════════════════════════════════════════════════════════╝

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║  🚀 HUNDEABOT V3 ULTRA - MAXIMUM POWER EDITION          ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado!
    echo 💡 Instala Python desde https://python.org
    pause
    exit /b 1
)

echo ✅ Python OK
echo.

REM Ask what to run
echo ¿Qué quieres ejecutar?
echo.
echo 1. ULTRA BOT (15+ fuentes con AI)
echo 2. Bot V3 normal (sin AI)
echo 3. Test AI Validator
echo 4. Quick Test
echo 5. Free Weekends
echo 6. Solo Epic Games
echo.

set /p choice="Elige (1-6): "

if "%choice%"=="1" goto ultra
if "%choice%"=="2" goto v3
if "%choice%"=="3" goto ai
if "%choice%"=="4" goto quick
if "%choice%"=="5" goto free
if "%choice%"=="6" goto epic
goto error

:ultra
echo.
echo 🚀 Ejecutando ULTRA BOT (Maximum Power)...
echo.
python hundea_v3_ultra.py
goto end

:v3
echo.
echo 🎮 Ejecutando Bot V3 (Standard)...
echo.
python hundea_v3.py
goto end

:ai
echo.
echo 🧠 Testing AI Validator...
echo.
python test_ai_validator.py
goto end

:quick
echo.
echo ⚡ Quick Test...
echo.
python quick_test.py
goto end

:free
echo.
echo 🆓 Free Weekends Hunter...
echo.
python run_free_weekends.py
goto end

:epic
echo.
echo ⭐ Solo Epic Games...
echo.
python -c "from modules.epic_hunter import EpicHunter; h = EpicHunter(); games = h.obtener_juegos_gratis(); print(f'\n✅ {len(games)} juegos gratis encontrados\n'); [print(f'{i}. {g[\"title\"]}') for i, g in enumerate(games, 1)]"
goto end

:error
echo.
echo ❌ Opción inválida
echo.
goto end

:end
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
