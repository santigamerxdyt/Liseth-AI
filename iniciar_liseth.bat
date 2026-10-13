@echo off
title Liseth • Asistente Personal
color 0B
echo ========================================================
echo         INICIANDO LISETH • ASISTENTE PERSONAL
echo ========================================================
echo.
echo Verificando entorno de Node.js...
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo [ALERTA] Node.js no se detecto en el sistema.
    echo Por favor instale Node.js desde https://nodejs.org/ para que el servidor funcione.
    echo.
    pause
    exit /b
)

echo [OK] Node.js detectado.
echo Levantando servidor y abriendo la interfaz en su navegador...
timeout /t 1 >nul
start "" http://localhost:3000
node server.js
pause
