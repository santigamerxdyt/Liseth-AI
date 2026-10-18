@echo off
chcp 65001 >nul
title Liseth AI - Sincronizador Automático con GitHub
color 0b

echo ==============================================================================
echo       LISETH AI - SINCRONIZACIÓN AUTOMÁTICA CON GITHUB
echo ==============================================================================
echo.
echo Sincronizando repositorio local con https://github.com/santigamerxdyt/Liseth-AI...
echo.

cd /d "%~dp0"

python -c "from app.services.git_sync_service import git_sync_service; res = git_sync_service.sync_to_github(); print(git_sync_service.format_report(res))"

echo.
echo ==============================================================================
echo Proceso finalizado. Presione cualquier tecla para cerrar esta ventana.
echo ==============================================================================
pause >nul
