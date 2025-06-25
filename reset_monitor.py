#!/usr/bin/env python3
# Script para resetar as barras de progresso na aba Monitor

import sys
from PyQt5 import QtWidgets, uic

def reset_monitor_bars():
    """Reseta todas as barras de progresso na aba Monitor"""
    # Carrega a UI
    app = QtWidgets.QApplication(sys.argv)
    window = uic.loadUi('microdrum.ui')
    
    # Lista de todas as barras de progresso
    progress_bars = [
        window.pbPin0, window.pbPin1, window.pbPin2, window.pbPin3,
        window.pbPin4, window.pbPin5, window.pbPin6, window.pbPin7,
        window.pbPin0_2, window.pbPin1_2, window.pbPin2_2, window.pbPin3_2,
        window.pbPin4_2, window.pbPin5_2, window.pbPin6_2, window.pbPin7_2,
        window.pbPin0_3, window.pbPin1_3, window.pbPin2_3, window.pbPin3_3,
        window.pbPin4_3, window.pbPin5_3, window.pbPin6_3, window.pbPin7_3,
        window.pbPin0_4, window.pbPin1_4, window.pbPin2_4, window.pbPin3_4,
        window.pbPin4_4, window.pbPin5_4, window.pbPin6_4, window.pbPin7_4,
        window.pbPin0_5, window.pbPin1_5, window.pbPin2_5, window.pbPin3_5,
        window.pbPin4_5, window.pbPin5_5, window.pbPin6_5, window.pbPin7_5,
        window.pbPin0_6, window.pbPin1_6, window.pbPin2_6, window.pbPin3_6,
        window.pbPin4_6, window.pbPin5_6, window.pbPin6_6, window.pbPin7_6
    ]
    
    # Reseta todas as barras
    for bar in progress_bars:
        bar.setValue(0)
    
    print("Todas as barras de progresso foram resetadas.")

if __name__ == "__main__":
    reset_monitor_bars()