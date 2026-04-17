@echo off
setlocal
title MINOS PRIME - Launcher

echo ==========================================
echo   MINOS PRIME - SISTEMA DE INTELIGENCIA
echo ==========================================
echo.

:: Intentar usar Windows Terminal (pestanas en la misma ventana)
where wt >nul 2>&1
if %errorlevel% == 0 (
    echo [WT] Abriendo en Windows Terminal...
    wt new-tab --title "MINOS Backend" cmd /k "cd /d "%~dp0" && uvicorn src.main:app --reload --port 8800" ^
    ; new-tab --title "MINOS Frontend" cmd /k "cd /d "%~dp0v0-financial-toro-dashboard-2-main\v0-financial-toro-dashboard-2-main" && npm run dev"
) else (
    echo [CMD] Windows Terminal no encontrado, usando ventanas separadas...
    start "MINOS Backend"  cmd /k "cd /d "%~dp0" && uvicorn src.main:app --reload --port 8800"
    timeout /t 3 /nobreak > nul
    start "MINOS Frontend" cmd /k "cd /d "%~dp0v0-financial-toro-dashboard-2-main\v0-financial-toro-dashboard-2-main" && npm run dev"
)

echo.
echo ------------------------------------------
echo [OK] Backend  -> http://localhost:8800
echo [OK] Frontend -> http://localhost:4400
echo ------------------------------------------
echo.
echo Presiona cualquier tecla para cerrar este lanzador.
pause > nul
