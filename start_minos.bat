@echo off
setlocal
title MINOS PRIME - Launcher

:: Definir rutas absolutas para evitar problemas con espacios
set "BASE_DIR=%~dp0"
set "FRONT_DIR=%BASE_DIR%v0-financial-toro-dashboard-2-main\v0-financial-toro-dashboard-2-main"

echo ==========================================
echo   MINOS PRIME - SISTEMA DE INTELIGENCIA
echo ==========================================
echo.

:: Detectar si Windows Terminal esta instalado
where wt >nul 2>&1
if %errorlevel% == 0 (
    echo [WT] Detectado Windows Terminal. Abriendo pestañas...
    :: Usamos --startingDirectory para evitar el "cd /d" con comillas anidadas que rompe el comando
    wt new-tab --title "MINOS Backend" --startingDirectory "%BASE_DIR%" cmd /k "uvicorn src.main:app --reload --port 8800" ; ^
    new-tab --title "MINOS Frontend" --startingDirectory "%FRONT_DIR%" cmd /k "npm run dev"
) else (
    echo [CMD] Windows Terminal no encontrado. Usando ventanas separadas...
    :: Backend
    start "MINOS Backend" /D "%BASE_DIR%" cmd /k "uvicorn src.main:app --reload --port 8800"
    
    timeout /t 3 /nobreak > nul
    
    :: Frontend
    start "MINOS Frontend" /D "%FRONT_DIR%" cmd /k "npm run dev"
)

echo.
echo ------------------------------------------
echo [OK] Backend  -> http://localhost:8800
echo [OK] Frontend -> http://localhost:4400
echo ------------------------------------------
echo.
echo Los servicios se estan ejecutando. 
echo Presiona cualquier tecla para cerrar este lanzador.
pause > nul
