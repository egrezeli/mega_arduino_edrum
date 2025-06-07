#!/bin/bash

# Script para organizar o projeto Mega Arduino eDrum

echo "Organizando o projeto Mega Arduino eDrum..."

# Criar pasta para ferramentas de desenvolvimento
mkdir -p dev_tools

# Mover arquivos de ferramentas para dev_tools
mv filter_notes.py dev_tools/ 2>/dev/null
mv midi_bridge.py dev_tools/ 2>/dev/null
mv midi_debug.py dev_tools/ 2>/dev/null
mv midi_direct_fix.py dev_tools/ 2>/dev/null
mv midi_monitor.py dev_tools/ 2>/dev/null
mv midi_translator.py dev_tools/ 2>/dev/null
mv midi_translator_enhanced.py dev_tools/ 2>/dev/null
mv serial_monitor.py dev_tools/ 2>/dev/null
mv check_fonts.py dev_tools/ 2>/dev/null
mv convert_to_spaces.py dev_tools/ 2>/dev/null
mv fix_buttons.py dev_tools/ 2>/dev/null
mv fix_indentation.py dev_tools/ 2>/dev/null
mv midi_fix.py dev_tools/ 2>/dev/null
mv fix_qvector.py dev_tools/ 2>/dev/null
mv testvirtualmidiport.py dev_tools/ 2>/dev/null
mv test_midi_virtual.py dev_tools/ 2>/dev/null
mv microdrum_config.py dev_tools/ 2>/dev/null
mv cleanup.sh dev_tools/ 2>/dev/null
mv run_with_fix.sh dev_tools/ 2>/dev/null

# Criar pasta para documentação
mkdir -p docs

# Mover arquivos de documentação para docs
mv README_FIXED.md docs/ 2>/dev/null
mv README_MACOS.md docs/ 2>/dev/null
mv README_PT.md docs/ 2>/dev/null
mv TROUBLESHOOTING.md docs/ 2>/dev/null
mv QVECTOR_FIX.md docs/ 2>/dev/null
mv error_fixes.md docs/ 2>/dev/null
mv snare_fix.md docs/ 2>/dev/null
mv MIDI_SETUP.md docs/ 2>/dev/null
mv INSTALL.md docs/ 2>/dev/null
mv CHANGELOG.md docs/ 2>/dev/null

# Renomear arquivos principais
cp microdrum.ui mega_arduino_edrum.ui 2>/dev/null

# Limpar arquivos temporários
rm -f *.pyc 2>/dev/null
rm -rf __pycache__ 2>/dev/null

echo "Organização concluída!"
