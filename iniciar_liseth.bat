@echo off
chcp 65001 >nul
title Liseth — Asistente Inteligente de Santiago
cd /d "%~dp0"

echo =====================================================================
echo                 LISETH — ASISTENTE INTELIGENTE
echo                      Arquitectura Python 2.0
echo =====================================================================
echo.

:: 1. Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] No se encontró Python en el sistema.
    echo Por favor instala Python 3.10 o superior y márcalo en el PATH.
    pause
    exit /b 1
)

:: 2. Preguntar o usar selección automática con temporizador
echo Selecciona cómo deseas iniciar a Liseth:
echo.
echo   [1] Modo Ventana Nativa de Escritorio (App independiente)
echo   [2] Modo Servidor Web + Celular PWA (Abre tu navegador)
echo   [3] Ejecutar pruebas del sistema (pytest)
echo.
echo Presiona 1, 2 o 3 (o espera 5 segundos para Modo Escritorio):

choice /c 123 /n /t 5 /d 1 /m "Tu opción [1, 2 o 3]: "
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
start "" "http://127.0.0.1:3000"
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
exit /b 0
