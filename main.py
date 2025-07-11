#!/usr/bin/env python3
#============================================================
#=>             Mega Arduino eDrum v1.0.0
#=>             github.com/yourusername/mega-arduino-edrum
#=>              CC BY-NC-SA 3.0
#=============================================================

import sys
import os

# import PyQt5 QtCore and QtGui modules
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from mainwindow import MainWindow

def fix_buttons(window):
    # Definir texto para os botões de upload (seta para cima)
    upload_buttons = [
        window.ui.pbUploadType, window.ui.pbUploadNote,
        window.ui.pbUploadThresold, window.ui.pbUploadScantime,
        window.ui.pbUploadMasktime, window.ui.pbUploadRetrigger,
        window.ui.pbUploadCurve, window.ui.pbUploadCurveform,
        window.ui.pbUploadXtalk, window.ui.pbUploadXtalkgroup,
        window.ui.pbUploadChannel, window.ui.pbUploadGain
    ]
    
    # Definir texto para os botões de download (seta para baixo)
    download_buttons = [
        window.ui.pbDownloadType, window.ui.pbDownloadNote,
        window.ui.pbDownloadThresold, window.ui.pbDownloadScantime,
        window.ui.pbDownloadMasktime, window.ui.pbDownloadRetrigger,
        window.ui.pbDownloadCurve, window.ui.pbDownloadCurveform,
        window.ui.pbDownloadXtalk, window.ui.pbDownloadXtalkgroup,
        window.ui.pbDownloadChannel, window.ui.pbDownloadGain
    ]
    
    # Aplicar texto de seta para cima
    for button in upload_buttons:
        button.setText("↑")
    
    # Aplicar texto de seta para baixo
    for button in download_buttons:
        button.setText("↓")

if __name__ == '__main__':

    # create application
    app = QApplication( sys.argv )
    app.setApplicationName( 'Mega Arduino eDrum' )
    
    # Aplicar folha de estilo para substituir fontes não disponíveis
    style_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'style.qss')
    if os.path.exists(style_path):
        with open(style_path, 'r') as f:
            app.setStyleSheet(f.read())

    # create widget
    w = MainWindow()
    w.setWindowTitle( 'Mega Arduino eDrum' )
    
    # Corrigir os botões de setas
    fix_buttons(w)
    
    w.show()

    # connection
    app.lastWindowClosed.connect(app.quit)
    
    # execute application
    sys.exit( app.exec_() )