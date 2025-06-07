#!/bin/bash

# Script para executar o MicroDrum Config Tool com a correção de QVector<int>

# Registrar o tipo QVector<int>
python3 fix_qvector.py

# Se o registro foi bem-sucedido, executar o programa principal
if [ $? -eq 0 ]; then
    echo "Iniciando MicroDrum Config Tool..."
    python3 main.py
else
    echo "Erro ao registrar o tipo QVector<int>. Verifique se o PyQt5 está instalado corretamente."
    exit 1
fi