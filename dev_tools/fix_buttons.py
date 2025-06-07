#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    fix_buttons(window)
    window.show()
    sys.exit(app.exec_())