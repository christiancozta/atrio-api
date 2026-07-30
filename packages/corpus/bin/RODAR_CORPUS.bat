@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ==========================================
echo    CORPUS - processando a pasta de entrada
echo ==========================================
echo.
py corpus_pseudonimizar.py --base ../
echo.
echo ------------------------------------------
py painel.py --base ../
echo ------------------------------------------
echo.
echo Concluido. O painel abriu no navegador.
echo Pode fechar esta janela.
pause
