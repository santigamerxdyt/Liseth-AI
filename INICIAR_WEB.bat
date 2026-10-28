@echo off
setlocal
cd /d "%~dp0"
title Liseth - Servidor Web

:: 1. Verificacion de Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] No se encontro Python en el sistema o en el PATH.
    echo Por favor instala Python 3.10+ o marcalo en el PATH de Windows.
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

echo [*] Iniciando servidor web de Liseth...
python run.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] El servidor de Liseth se detuvo (Codigo de salida: %errorlevel%).
    echo Revisa los mensajes anteriores para identificar el motivo.
    pause
)
endlocal
