@echo off
setlocal
title MINOS PRIME - Launcher

set "ROOT=%~dp0"
set "BACK=%ROOT%"
set "FRONT=%ROOT%frontend\client"

echo ==========================================
echo   MINOS PRIME - SISTEMA DE INTELIGENCIA
echo ==========================================
echo.

if not exist "%BACK%\src\main.py" (
    echo [ERROR] No se encontro src\main.py en:
    echo %BACK%
    pause
    exit /b 1
)

if not exist "%FRONT%\package.json" (
    echo [ERROR] No se encontro package.json en:
    echo %FRONT%
    pause
    exit /b 1
)

echo [1] Levantando Backend en http://localhost:8800...
start "MINOS Backend" /D "%BACK%" cmd /k py -3.12 -m uvicorn src.main:app --reload --port 8800

timeout /t 4 /nobreak >nul

echo [2] Levantando Frontend en http://localhost:4400...
start "MINOS Frontend" /D "%FRONT%" cmd /k npm.cmd run dev

timeout /t 4 /nobreak >nul

echo [3] Abriendo Chrome en http://localhost:4400 ...
start chrome "http://localhost:4400"
start chrome "http://localhost:8800/docs"

echo.
echo ------------------------------------------
echo [OK] Backend  = http://localhost:8800
echo [OK] Frontend = http://localhost:4400
echo ------------------------------------------
echo.
echo Presiona cualquier tecla para cerrar.
pause >nul
