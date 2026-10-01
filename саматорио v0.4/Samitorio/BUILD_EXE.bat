@echo off
setlocal
title Samitorio v0.4 - Build EXE
chcp 65001 >nul
cd /d "%~dp0"
python -c "import pygame" >nul 2>nul || python -m pip install --upgrade pygame-ce
python -m pip show pyinstaller >nul 2>nul
if errorlevel 1 python -m pip install pyinstaller
python -m PyInstaller --onefile --windowed --name Samitorio-v04 main.py
if errorlevel 1 (
    echo Build failed. See error above.
)
if exist "dist\Samitorio-v04.exe" (
    echo.
    echo Build OK: dist\Samitorio-v04.exe  (requires running device with pygame-ce bundled libs)
)
pause
