@echo off
chcp 65001 >nul
cd /d "%~dp0"
py captura.py --base ../
echo.
echo Pode fechar esta janela.
pause
