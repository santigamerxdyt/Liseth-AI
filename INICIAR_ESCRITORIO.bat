@echo off
chcp 65001 >nul
title Liseth — Aplicación de Escritorio
cd /d "%~dp0"
python run.py --desktop
