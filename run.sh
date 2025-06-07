#!/bin/bash
# Script para executar o Mega Arduino eDrum

# Verifica se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Python 3 não encontrado. Por favor, instale o Python 3."
    exit 1
fi

# Verifica se as dependências estão instaladas
python3 -c "import PyQt5, serial, rtmidi" &> /dev/null
if [ $? -ne 0 ]; then
    echo "Instalando dependências..."
    pip install -r requirements.txt
fi

# Executa o programa
python3 main.py