@echo off
REM ╔══════════════════════════════════════════════════════╗
REM ║  🧪 TEST LOCAL - Antes de Commit                    ║
REM ╚══════════════════════════════════════════════════════╝

echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║  🧪 LOCAL TEST - Pre-Commit Verification            ║
echo ║  Evita runs innecesarios en GitHub Actions          ║
echo ╚══════════════════════════════════════════════════════╝
echo.

echo ⚙️  Ejecutando tests locales...
echo.

python test_local_before_commit.py

if %ERRORLEVEL% == 0 (
    echo.
    echo ════════════════════════════════════════════════════════
    echo.
    echo ✅ TESTS PASSED! Ready para commit
    echo.
    echo ¿Hacer commit y push ahora? (s/n^)
    set /p commit="→ "
    
    if /i "%commit%"=="s" (
        echo.
        echo 📝 Haciendo commit...
        git add modules/core/scoring.py hundea_v3_ultra.py
        git commit -m "fix: Support ConsoleDeal in scoring + ULTRA bot"
        echo.
        echo 📤 Haciendo push...
        git push
        echo.
        echo 🎉 DONE! GitHub Actions se ejecutará automáticamente
    ) else (
        echo.
        echo 💡 OK, puedes hacer commit manual cuando quieras:
        echo    git add modules/core/scoring.py hundea_v3_ultra.py
        echo    git commit -m "fix: Support ConsoleDeal in scoring"
        echo    git push
    )
) else (
    echo.
    echo ════════════════════════════════════════════════════════
    echo.
    echo ❌ TESTS FAILED! NO hacer commit todavía
    echo.
    echo Revisa los errores arriba y arregla antes de commit
)

echo.
pause
