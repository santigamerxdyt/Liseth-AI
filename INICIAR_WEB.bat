@echo off
cd /d "%~dp0"
title Liseth - Servidor Web (Modo Administrador)

:: Verificacion y Elevacion Automatica a Modo Administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Solicitando privilegios de Administrador para Liseth...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -ArgumentList '%*' -Verb RunAs"
    exit /b 0
)

start http://127.0.0.1:3000
python run.py
