@echo off
setlocal
title Samitorio v0.4
chcp 65001 >nul
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found in PATH. Install Python 3.12+.
    pause
    exit /b 1
)
python -c "import pygame" >nul 2>nul
if errorlevel 1 (
    echo Pygame was not found, installing pygame-ce...
    python -m pip install --upgrade pygame-ce
)
python -c "import pygame; print('pygame OK:', pygame.version.ver)"
python main.py
pause
