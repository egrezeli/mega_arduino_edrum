#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFontDatabase

app = QApplication(sys.argv)
font_db = QFontDatabase()
print("Fontes disponíveis:")
for font in font_db.families():
    print(f"- {font}")