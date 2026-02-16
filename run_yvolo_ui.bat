@echo off
REM Cambia al directorio donde está este .bat
cd /d %~dp0

where pythonw >nul 2>nul
if errorlevel 1 (
    echo pythonw no encontrado en PATH. Instala Python o ajusta tu PATH.
    exit /b 1
)

REM Ejecuta la UI sin consola
start "yvolo UI" /b pythonw ui_main.py
