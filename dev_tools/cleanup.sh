#!/bin/bash

# Script para limpar arquivos desnecessários do projeto

# Arquivos a serem mantidos
KEEP_FILES=(
  "main.py"
  "mainwindow.py"
  "microdrum.ui"
  "midi_wrapper.py"
  "pins.ini"
  "README.md"
  "README_MACOS.md"
  "requirements.txt"
  "run.sh"
  "style.qss"
  "LICENSE"
  "logo.png"
)

# Arquivos temporários ou de desenvolvimento que podem ser removidos
TEMP_FILES=(
  "check_fonts.py"
  "convert_to_spaces.py"
  "fix_buttons.py"
  "fix_indentation.py"
  "microdrum_config.py"
  "midi_fix.py"
  "test_midi_virtual.py"
  "testvirtualmidiport.py"
  "ui_microdrum.py"
  "README_PT.md"
)

echo "Arquivos que serão mantidos:"
for file in "${KEEP_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "  - $file"
  fi
done

echo -e "\nArquivos que serão movidos para pasta 'dev_tools':"
mkdir -p dev_tools
for file in "${TEMP_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "  - $file"
    mv "$file" dev_tools/
  fi
done

echo -e "\nLimpeza concluída. Arquivos de desenvolvimento foram movidos para a pasta 'dev_tools'."
