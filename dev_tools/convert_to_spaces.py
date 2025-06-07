#!/usr/bin/env python3

# Script para converter todos os tabs para espaços no arquivo mainwindow.py
with open('mainwindow.py', 'r') as file:
    content = file.read()

# Substituir todos os tabs por 4 espaços
content = content.replace('\t', '    ')

with open('mainwindow.py', 'w') as file:
    file.write(content)

print("Todos os tabs foram convertidos para espaços")
