@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ==========================================
echo    ATRIO - verificando dependencias
echo ==========================================
echo.
py verificar_dependencias.py
echo.
echo Pode fechar esta janela.
pause
