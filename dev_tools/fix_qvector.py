#!/usr/bin/env python3
"""
Script para corrigir o erro de QVector<int> no MicroDrum Config Tool
"""

import sys
from PyQt5.QtCore import QCoreApplication, qRegisterMetaType

def main():
    """Registra o tipo QVector<int> para uso em sinais/slots entre threads"""
    # Criar uma aplicação Qt (necessário para o sistema de meta-objetos)
    app = QCoreApplication([])
    
    # Registrar o tipo QVector<int>
    qRegisterMetaType("QVector<int>")
    
    print("Tipo QVector<int> registrado com sucesso!")
    print("Agora você pode executar o MicroDrum Config Tool normalmente.")
    
    # Não é necessário entrar no loop de eventos
    return 0

if __name__ == "__main__":
    sys.exit(main())