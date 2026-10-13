@echo off
chcp 65001 >nul
title Liseth — Servidor Web
cd /d "%~dp0"
start "" "http://127.0.0.1:3000"
python run.py
