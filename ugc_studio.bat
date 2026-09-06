@echo off
chcp 65001 >nul
title UGC Production Studio
python tools\menu.py
if %errorlevel% neq 0 (
    echo.
    echo Ocurrio un error al ejecutar el centro de control.
    echo Asegurate de haber ejecutado primero: install_and_setup.bat
    pause
)
