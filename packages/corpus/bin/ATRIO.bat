@echo off
chcp 65001 >nul
cd /d "%~dp0"

:menu
cls
echo ==========================================
echo    ATRIO - CORPUS
echo ==========================================
echo.
echo   1  Rodar o CORPUS  (processa a entrada e abre o painel)
echo   2  Rodar o OCR     (PDF escaneado que ficou esperando)
echo   3  Gerar inventario em Excel
echo   4  Abrir o painel
echo   5  Verificar dependencias
echo.
echo   0  Sair
echo.
set "op="
set /p op=Escolha uma opcao e tecle Enter:

if "%op%"=="1" goto corpus
if "%op%"=="2" goto ocr
if "%op%"=="3" goto inventario
if "%op%"=="4" goto painel
if "%op%"=="5" goto verificar
if "%op%"=="0" goto fim
echo.
echo Opcao invalida.
pause
goto menu

:corpus
echo.
py corpus_pseudonimizar.py --base ../
echo.
py painel.py --base ../
goto fimlinha

:ocr
echo.
py ocr_pendentes.py --base ../
goto fimlinha

:inventario
echo.
py exportar_inventario.py --base ../
goto fimlinha

:painel
echo.
py painel.py --base ../
goto fimlinha

:verificar
echo.
py verificar_dependencias.py
goto fimlinha

:fimlinha
echo.
echo ------------------------------------------
pause
goto menu

:fim
