#!/usr/bin/env python3

# Script para corrigir problemas de indentação no arquivo mainwindow.py
with open('mainwindow.py', 'r') as file:
    lines = file.readlines()

with open('mainwindow_fixed.py', 'w') as file:
    for line in lines:
        # Substituir espaços por tabs onde necessário
        if line.startswith('        '):
            line = '\t' + line[8:]
        file.write(line)

print("Arquivo corrigido criado como mainwindow_fixed.py")
