@echo off
setlocal
cd /d "%~dp0"
title Liseth - Asistente Inteligente

:: 1. Verificacion de Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] No se encontro Python en el sistema o en el PATH.
    echo Por favor instala Python 3.10 o superior y marcalo en el PATH de Windows.
    pause
    exit /b 1
)

:: 2. Verificacion y Elevacion Opcional a Administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Verificando privilegios de Administrador para control de hardware y sistema...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -ArgumentList '%*' -WorkingDirectory '%~dp0' -Verb RunAs" 2>nul
    if %errorlevel% equ 0 exit /b 0
    echo [!] Elevacion UAC omitida o cancelada. Iniciando Liseth en Modo Estandar...
)

cls

echo =====================================================================
echo                 LISETH - ASISTENTE INTELIGENTE
echo                      Arquitectura Python 2.0
echo =====================================================================
echo.

:: 3. Preguntar o usar seleccion automatica con temporizador
echo Selecciona como deseas iniciar a Liseth:
echo.
echo   [1] Modo Ventana Nativa de Escritorio (App independiente)
echo   [2] Modo Servidor Web (Abre tu navegador predeterminado)
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
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Liseth se cerro inesperadamente (Codigo %errorlevel%).
    pause
)
goto FIN

:MODO_WEB
echo [*] Iniciando servidor web de Liseth...
python run.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] El servidor web de Liseth se detuvo (Codigo %errorlevel%).
    pause
)
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
