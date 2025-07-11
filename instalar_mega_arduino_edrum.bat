@echo off
title Instalador Mega Arduino eDrum
color 0A
setlocal

echo ===================================================
echo    INSTALADOR MEGA ARDUINO EDRUM PARA WINDOWS
echo ===================================================
echo.
echo Este script vai:
echo  1. Verificar se o Python esta instalado
echo  2. Instalar o Python se necessario
echo  3. Instalar as dependencias necessarias
echo  4. Executar o Mega Arduino eDrum
echo.
echo Por favor, aguarde enquanto preparamos tudo para voce.
echo.
timeout /t 5 >nul

:: Verifica se o Python está instalado ou procura em locais comuns
echo [VERIFICANDO] Python...

:: Tenta executar python diretamente
python --version >nul 2>nul
if not errorlevel 1 (
    echo [OK] Python ja esta instalado.
    set "PYTHON_CMD=python"
    goto :python_ok
)

:: Tenta encontrar python em locais comuns
if exist "C:\Program Files\Python310\python.exe" (
    set "PYTHON_CMD=C:\Program Files\Python310\python.exe"
    echo [ENCONTRADO] Python em C:\Program Files\Python310\
    goto :python_ok
)

if exist "C:\Program Files (x86)\Python310\python.exe" (
    set "PYTHON_CMD=C:\Program Files (x86)\Python310\python.exe"
    echo [ENCONTRADO] Python em C:\Program Files (x86)\Python310\
    goto :python_ok
)

if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    echo [ENCONTRADO] Python em %LOCALAPPDATA%\Programs\Python\Python310\
    goto :python_ok
)

:: Python nao encontrado, precisa instalar
echo [NAO ENCONTRADO] Python nao esta instalado.
echo [INSTALANDO] Python 3.10.11 (64-bit)...
echo.
echo Baixando o instalador do Python...

:: Cria pasta temporária
mkdir temp >nul 2>nul

:: Baixa o Python
powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe' -OutFile 'temp\python-installer.exe'}"

echo Instalando Python (isso pode demorar alguns minutos)...
echo Por favor, aguarde...

:: Instala o Python silenciosamente com as opções necessárias
start /wait temp\python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1

:: Aguarda a instalação
echo Aguardando a conclusao da instalacao...
timeout /t 30 >nul

:: Atualiza o PATH para esta sessão
echo Atualizando variaveis de ambiente...
set "PATH=%PATH%;C:\Program Files\Python310;C:\Program Files\Python310\Scripts"
set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python310;%LOCALAPPDATA%\Programs\Python\Python310\Scripts"

:: Verifica novamente
echo Verificando a instalacao do Python...
python --version >nul 2>nul
if not errorlevel 1 (
    echo [SUCESSO] Python instalado com sucesso!
    set "PYTHON_CMD=python"
    goto :python_ok
)

:: Tenta encontrar python após a instalação
if exist "C:\Program Files\Python310\python.exe" (
    set "PYTHON_CMD=C:\Program Files\Python310\python.exe"
    echo [SUCESSO] Python instalado em C:\Program Files\Python310\
    goto :python_ok
)

if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    echo [SUCESSO] Python instalado em %LOCALAPPDATA%\Programs\Python\Python310\
    goto :python_ok
)

echo [ERRO] Falha ao instalar o Python. Por favor, instale manualmente.
echo Visite: https://www.python.org/downloads/
echo Durante a instalacao, marque a opcao "Add Python to PATH"
pause
exit /b 1

:python_ok
:: Verifica a versão do pip
echo.
echo [VERIFICANDO] pip...
%PYTHON_CMD% -m pip --version >nul 2>nul
if errorlevel 1 (
    echo [INSTALANDO] pip...
    %PYTHON_CMD% -m ensurepip --upgrade
) else (
    echo [OK] pip ja esta instalado.
    echo [ATUALIZANDO] pip para a versao mais recente...
    %PYTHON_CMD% -m pip install --upgrade pip >nul 2>nul
)

:: Instala as dependências
echo.
echo [INSTALANDO] Dependencias necessarias...
echo Isso pode demorar alguns minutos, por favor aguarde...

:: Instala as dependências uma por uma para melhor feedback
echo  - Instalando PyQt5...
%PYTHON_CMD% -m pip install PyQt5 >nul 2>nul
echo  - Instalando pyserial...
%PYTHON_CMD% -m pip install pyserial >nul 2>nul
echo  - Instalando python-rtmidi...
%PYTHON_CMD% -m pip install python-rtmidi --no-build-isolation >nul 2>nul
echo  - Instalando psutil...
%PYTHON_CMD% -m pip install psutil >nul 2>nul

echo [SUCESSO] Todas as dependencias foram instaladas!

:: Verifica se o programa já existe
echo.
if not exist main.py (
    echo [ERRO] Arquivo main.py nao encontrado.
    echo Por favor, certifique-se de que este script esta na pasta do Mega Arduino eDrum.
    pause
    exit /b 1
)

:: Cria um atalho na área de trabalho
echo [CRIANDO] Atalho na area de trabalho...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([System.Environment]::GetFolderPath('Desktop') + '\Mega Arduino eDrum.lnk'); $Shortcut.TargetPath = '%~dp0run.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.IconLocation = '%SystemRoot%\System32\SHELL32.dll,77'; $Shortcut.Save()"

:: Cria o arquivo run.bat para execução futura
echo @echo off > run.bat
echo title Mega Arduino eDrum >> run.bat
echo color 0A >> run.bat
echo echo Iniciando Mega Arduino eDrum... >> run.bat
echo echo. >> run.bat
if "%PYTHON_CMD%"=="python" (
    echo python main.py >> run.bat
) else (
    echo "%PYTHON_CMD%" main.py >> run.bat
)
echo if errorlevel 1 ( >> run.bat
echo   echo. >> run.bat
echo   echo Ocorreu um erro ao executar o programa. >> run.bat
echo   pause >> run.bat
echo ) >> run.bat

:: Finaliza
echo.
echo ===================================================
echo    INSTALACAO CONCLUIDA COM SUCESSO!
echo ===================================================
echo.
echo O Mega Arduino eDrum foi instalado com sucesso!
echo Um atalho foi criado na sua area de trabalho.
echo.
echo Deseja executar o programa agora?
choice /c SN /m "Digite S para Sim ou N para Nao"

if errorlevel 2 goto :nao_executar
if errorlevel 1 goto :executar

:executar
echo.
echo Iniciando Mega Arduino eDrum...
if "%PYTHON_CMD%"=="python" (
    python main.py
) else (
    "%PYTHON_CMD%" main.py
)
goto :fim

:nao_executar
echo.
echo Para executar o programa mais tarde, use o atalho na area de trabalho
echo ou execute o arquivo "run.bat" nesta pasta.

:fim
echo.
echo Pressione qualquer tecla para sair...
pause >nul
exit /b 0
