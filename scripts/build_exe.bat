@echo off
chcp 65001 >nul
title Construir Nebula Executable

cd /d "%~dp0.."

echo Limpiando builds anteriores...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo.
echo Instalando PyInstaller si no esta...
pip install pyinstaller

echo.
echo Construyendo ejecutable...
python -m PyInstaller --onefile --windowed --name "Nebula" --icon "assets\Nebula-Ovni.ico" --add-data "assets;assets" --hidden-import "PIL._tkinter_finder" --collect-all "styles" --collect-all "metadata_styles" main.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Fallo la construccion.
    pause
    exit /b 1
)

echo.
echo Ejecutable creado: dist\Nebula.exe
echo.
pause
