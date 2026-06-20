@echo off
title Editor de Analisis Visual Cientifico-Tecnico
cd /d "%~dp0"
python main.py
if %errorlevel% neq 0 (
    echo.
    echo Ocurrio un error. Verifica que Python esta instalado.
    echo Instala las dependencias con: pip install -r requirements.txt
    pause
)
