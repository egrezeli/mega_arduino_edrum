#!/usr/bin/env python3
"""
Monitor MIDI simples para testar a comunicação entre o MicroDrum e o IAC Driver
"""

import sys
import time
import rtmidi
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QComboBox, QPushButton, QLabel, QTextEdit, QWidget)
from PyQt5.QtCore import QThread, pyqtSignal, Qt

class MidiMonitorThread(QThread):
    """Thread para monitorar mensagens MIDI"""
    midi_message = pyqtSignal(list, float)
    
    def __init__(self, port_index):
        super().__init__()
        self.port_index = port_index
        self.running = True
        
    def run(self):
        """Executa o monitoramento MIDI"""
        try:
            midi_in = rtmidi.MidiIn()
            if self.port_index >= 0 and self.port_index < midi_in.get_port_count():
                midi_in.open_port(self.port_index)
                
                while self.running:
                    msg = midi_in.get_message()
                    if msg:
                        message, deltatime = msg
                        self.midi_message.emit(message, deltatime)
                    time.sleep(0.001)
                    
                midi_in.close_port()
        except Exception as e:
            print(f"Erro no thread MIDI: {e}")
            
    def stop(self):
        """Para o monitoramento"""
        self.running = False
        self.wait()

class MidiMonitorWindow(QMainWindow):
    """Janela principal do monitor MIDI"""
    
    def __init__(self):
        super().__init__()
        self.monitor_thread = None
        self.initUI()
        
    def initUI(self):
        """Inicializa a interface do usuário"""
        self.setWindowTitle("Monitor MIDI para MicroDrum")
        self.setGeometry(100, 100, 600, 400)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Área de controle
        control_layout = QHBoxLayout()
        
        # Seletor de porta MIDI
        self.port_label = QLabel("Porta MIDI:")
        self.port_combo = QComboBox()
        self.refresh_button = QPushButton("Atualizar")
        self.refresh_button.clicked.connect(self.refresh_ports)
        self.start_button = QPushButton("Iniciar Monitoramento")
        self.start_button.clicked.connect(self.toggle_monitoring)
        
        control_layout.addWidget(self.port_label)
        control_layout.addWidget(self.port_combo)
        control_layout.addWidget(self.refresh_button)
        control_layout.addWidget(self.start_button)
        
        # Área de log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        
        # Adicionar layouts ao layout principal
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.log_text)
        
        # Inicializar lista de portas
        self.refresh_ports()
        
    def refresh_ports(self):
        """Atualiza a lista de portas MIDI disponíveis"""
        self.port_combo.clear()
        
        midi_in = rtmidi.MidiIn()
        ports = midi_in.get_ports()
        
        if ports:
            for port in ports:
                self.port_combo.addItem(port)
            
            # Selecionar automaticamente porta IAC se disponível
            for i, port in enumerate(ports):
                if "IAC" in port:
                    self.port_combo.setCurrentIndex(i)
                    break
        else:
            self.log_message("Nenhuma porta MIDI de entrada encontrada")
            
    def toggle_monitoring(self):
        """Inicia ou para o monitoramento MIDI"""
        if self.monitor_thread and self.monitor_thread.running:
            self.stop_monitoring()
            self.start_button.setText("Iniciar Monitoramento")
        else:
            self.start_monitoring()
            self.start_button.setText("Parar Monitoramento")
            
    def start_monitoring(self):
        """Inicia o monitoramento MIDI"""
        if self.port_combo.count() == 0:
            self.log_message("Nenhuma porta MIDI disponível")
            return
            
        port_index = self.port_combo.currentIndex()
        port_name = self.port_combo.currentText()
        
        self.log_message(f"Iniciando monitoramento na porta: {port_name}")
        
        # Parar thread anterior se existir
        if self.monitor_thread:
            self.monitor_thread.stop()
            
        # Iniciar nova thread
        self.monitor_thread = MidiMonitorThread(port_index)
        self.monitor_thread.midi_message.connect(self.handle_midi_message)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Para o monitoramento MIDI"""
        if self.monitor_thread:
            self.monitor_thread.stop()
            self.log_message("Monitoramento parado")
            
    def handle_midi_message(self, message, deltatime):
        """Manipula mensagens MIDI recebidas"""
        if len(message) >= 3:
            status_byte = message[0]
            data1 = message[1]
            data2 = message[2]
            
            if (status_byte & 0xF0) == 0x90:  # Note On
                channel = status_byte & 0x0F
                self.log_message(f"Note On - Canal: {channel+1}, Nota: {data1}, Velocidade: {data2}")
            elif (status_byte & 0xF0) == 0x80:  # Note Off
                channel = status_byte & 0x0F
                self.log_message(f"Note Off - Canal: {channel+1}, Nota: {data1}, Velocidade: {data2}")
            elif (status_byte & 0xF0) == 0xB0:  # Control Change
                channel = status_byte & 0x0F
                self.log_message(f"Control Change - Canal: {channel+1}, Controle: {data1}, Valor: {data2}")
            else:
                self.log_message(f"Mensagem MIDI: {message}")
        else:
            self.log_message(f"Mensagem MIDI: {message}")
            
    def log_message(self, message):
        """Adiciona uma mensagem ao log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
    def closeEvent(self, event):
        """Manipula o evento de fechamento da janela"""
        if self.monitor_thread:
            self.monitor_thread.stop()
        event.accept()

def main():
    """Função principal"""
    app = QApplication(sys.argv)
    window = MidiMonitorWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()