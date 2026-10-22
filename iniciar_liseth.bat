@echo off
setlocal
cd /d "%~dp0"
title Liseth - Asistente Personal (Modo Administrador)

:: 0. Verificacion y Elevacion Automatica a Modo Administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Solicitando privilegios de Administrador para Liseth...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -ArgumentList '%*' -Verb RunAs"
    exit /b 0
)

cls

echo =====================================================================
echo                 LISETH - ASISTENTE INTELIGENTE
echo               [Modo Administrador - Acceso Total]
echo                      Arquitectura Python 2.0
echo =====================================================================
echo.

:: 1. Verificar si Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] No se encontro Python en el sistema.
    echo Por favor instala Python 3.10 o superior y marcalo en el PATH.
    pause
    exit /b 1
)

:: 2. Preguntar o usar seleccion automatica con temporizador
echo Selecciona como deseas iniciar a Liseth:
echo.
echo   [1] Modo Ventana Nativa de Escritorio (App independiente)
echo   [2] Modo Servidor Web (Abre tu navegador)
echo   [3] Ejecutar pruebas del sistema (pytest)
echo.
echo Presiona 1, 2 o 3 (o espera 5 segundos para Modo Escritorio):

choice /c 123 /n /t 5 /d 1 /m "Tu opcion [1, 2 o 3]: "
set OP=%errorlevel%

echo.
if "%OP%"=="1" goto MODO_ESCRITORIO
if "%OP%"=="2" goto MODO_WEB
if "%OP%"=="3" goto MODO_TEST

:MODO_ESCRITORIO
echo [*] Iniciando Liseth en ventana nativa de escritorio...
python run.py --desktop
goto FIN

:MODO_WEB
echo [*] Iniciando servidor web de Liseth...
python run.py
goto FIN

:MODO_TEST
echo [*] Ejecutando suite de pruebas automatizadas...
python -m pytest test/ -v
echo.
echo Presiona cualquier tecla para salir...
pause >nul
goto FIN

:FIN
endlocal
exit /b 0
