@echo off
cd /d "%~dp0"
title Liseth - Servidor Web
start http://127.0.0.1:3000
python run.py
