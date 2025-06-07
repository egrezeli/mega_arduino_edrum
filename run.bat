@echo off
REM Script para executar o Mega Arduino eDrum no Windows

REM Verifica se o Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python nao encontrado. Por favor, instale o Python 3.
    pause
    exit /b 1
)

REM Verifica se as dependências estão instaladas
python -c "import PyQt5, serial, rtmidi" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Instalando dependencias...
    pip install -r requirements.txt
)

REM Executa o programa
python main.py
pause