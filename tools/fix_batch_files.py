import os

iniciar_liseth_content = """@echo off
setlocal
cd /d "%~dp0"
title Liseth - Asistente Personal
cls

echo =====================================================================
echo                 LISETH - ASISTENTE INTELIGENTE
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
start http://127.0.0.1:3000
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
"""

iniciar_escritorio_content = """@echo off
cd /d "%~dp0"
title Liseth - Aplicacion de Escritorio
python run.py --desktop
"""

iniciar_web_content = """@echo off
cd /d "%~dp0"
title Liseth - Servidor Web
start http://127.0.0.1:3000
python run.py
"""

# Write all as CRLF ASCII
def write_bat(filename, content):
    crlf_content = content.replace("\r\n", "\n").replace("\n", "\r\n")
    with open(filename, "wb") as f:
        f.write(crlf_content.encode("ascii"))
    print(f"Wrote {filename} with {len(crlf_content)} bytes (CRLF ASCII)")

write_bat("iniciar_liseth.bat", iniciar_liseth_content)
write_bat("INICIAR_ESCRITORIO.bat", iniciar_escritorio_content)
write_bat("INICIAR_WEB.bat", iniciar_web_content)
