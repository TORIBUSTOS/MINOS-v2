@echo off
setlocal
title MINOS PRIME - Launcher

set "FRONT=C:\Users\mauri\OneDrive\Escritorio\TORO\_TORO _HOLDING_\55 - Proyectos-TORO v2\2_MINOS_v2\v0-financial-toro-dashboard-2-main\v0-financial-toro-dashboard-2-main"
set "BACK=C:\Users\mauri\OneDrive\Escritorio\TORO\_TORO _HOLDING_\55 - Proyectos-TORO v2\2_MINOS_v2"

echo ==========================================
echo   MINOS PRIME - SISTEMA DE INTELIGENCIA
echo ==========================================
echo.

if not exist "%FRONT%\package.json" (
    echo [ERROR] No se encontro package.json en:
    echo %FRONT%
    pause
    exit /b
)

echo [1] Levantando Backend en http://localhost:8800...
start "MINOS Backend" /D "%BACK%" cmd /k uvicorn src.main:app --reload --port 8800

timeout /t 2 /nobreak >nul

echo [2] Levantando Frontend en http://localhost:4400...
start "MINOS Frontend" /D "%FRONT%" cmd /k npm run dev

echo.
echo ------------------------------------------
echo [OK] Backend  = http://localhost:8800
echo [OK] Frontend = http://localhost:4400
echo ------------------------------------------
echo.
echo Presiona cualquier tecla para cerrar.
pause >nul