@echo off
:: Nome da pasta do ambiente virtual
SET VENV_DIR=venv
:: Lista de bibliotecas a serem instaladas
SET LIBS=matplotlib numpy ttkthemes

:: Verifica se a pasta venv ja existe
if not exist %VENV_DIR% (
    echo [INFO] Ambiente virtual nao encontrado. Iniciando setup...
    python -m venv %VENV_DIR%
    
    echo [INFO] Instalando dependencias do requirements.txt...
    call %VENV_DIR%\Scripts\activate
    pip install %LIBS%
    
    echo [INFO] Setup concluido com sucesso!
) 

else (
    echo [INFO] Ambiente detectado. Preparando para rodar...
    call %VENV_DIR%\Scripts\activate
)

:: Executa o programa
echo [INFO] Iniciando o programa...
python main.py

:: Mantem a janela aberta se houver erro no Python
if %errorlevel% neq 0 (
    echo.
    echo [ERRO] O programa fechou com erro de codigo: %errorlevel%
    pause
)