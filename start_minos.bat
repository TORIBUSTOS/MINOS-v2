@echo off
setlocal
title MINOS PRIME - Launcher

echo ==========================================
echo   MINOS PRIME - SISTEMA DE INTELIGENCIA
echo ==========================================
echo.

:: --- FRONTEND (Antigravity) ---
echo [AG] Levantando Frontend en http://localhost:4400...
:: Se usa 'start' para que no bloquee la ejecucion del resto del script
start "MINOS Frontend" cmd /k "cd v0-financial-toro-dashboard-2-main\v0-financial-toro-dashboard-2-main && npm run dev"

echo.
echo ------------------------------------------
echo [CLAUDE] Backend pendiente de configuracion.
echo ------------------------------------------
echo.

echo El frontend se esta iniciando en una nueva ventana.
echo Presiona cualquier tecla cuando desees cerrar este lanzador.
pause > nul
