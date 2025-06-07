#!/usr/bin/env python3
"""
Monitor Serial para MicroDrum - Verifica se o Arduino está enviando dados MIDI
"""

import sys
import time
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QComboBox, QPushButton, QLabel, QTextEdit, QWidget,
                            QSpinBox)
from PyQt5.QtCore import QThread, pyqtSignal, Qt

class SerialMonitorThread(QThread):
    """Thread para monitorar mensagens da porta serial"""
    serial_data = pyqtSignal(bytes)
    serial_error = pyqtSignal(str)
    
    def __init__(self, port, baud_rate):
        super().__init__()
        self.port = port
        self.baud_rate = baud_rate
        self.running = True
        
    def run(self):
        """Executa o monitoramento serial"""
        try:
            ser = serial.Serial(self.port, self.baud_rate, timeout=0.1)
            
            while self.running:
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting)
                    if data:
                        self.serial_data.emit(data)
                time.sleep(0.01)
                
            ser.close()
        except Exception as e:
            self.serial_error.emit(str(e))
            
    def stop(self):
        """Para o monitoramento"""
        self.running = False
        self.wait()

class SerialMonitorWindow(QMainWindow):
    """Janela principal do monitor serial"""
    
    def __init__(self):
        super().__init__()
        self.monitor_thread = None
        self.initUI()
        
    def initUI(self):
        """Inicializa a interface do usuário"""
        self.setWindowTitle("Monitor Serial para MicroDrum")
        self.setGeometry(100, 100, 700, 500)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Área de controle
        control_layout = QHBoxLayout()
        
        # Seletor de porta serial
        self.port_label = QLabel("Porta Serial:")
        self.port_combo = QComboBox()
        
        # Seletor de baud rate
        self.baud_label = QLabel("Baud Rate:")
        self.baud_combo = QComboBox()
        for baud in [9600, 19200, 31250, 38400, 57600, 115200]:
            self.baud_combo.addItem(str(baud))
        self.baud_combo.setCurrentText("115200")  # Padrão para MicroDrum
        
        # Botões
        self.refresh_button = QPushButton("Atualizar")
        self.refresh_button.clicked.connect(self.refresh_ports)
        self.start_button = QPushButton("Iniciar Monitoramento")
        self.start_button.clicked.connect(self.toggle_monitoring)
        self.clear_button = QPushButton("Limpar")
        self.clear_button.clicked.connect(self.clear_log)
        
        # Adicionar widgets ao layout de controle
        control_layout.addWidget(self.port_label)
        control_layout.addWidget(self.port_combo)
        control_layout.addWidget(self.baud_label)
        control_layout.addWidget(self.baud_combo)
        control_layout.addWidget(self.refresh_button)
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.clear_button)
        
        # Opções de visualização
        view_layout = QHBoxLayout()
        self.view_label = QLabel("Visualização:")
        self.view_combo = QComboBox()
        self.view_combo.addItems(["Hexadecimal", "ASCII", "Decimal", "MIDI"])
        self.view_combo.setCurrentText("MIDI")
        
        view_layout.addWidget(self.view_label)
        view_layout.addWidget(self.view_combo)
        view_layout.addStretch()
        
        # Área de log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QTextEdit.NoWrap)
        self.log_text.setStyleSheet("font-family: Menlo, Monaco, Courier, monospace;")
        
        # Adicionar layouts ao layout principal
        main_layout.addLayout(control_layout)
        main_layout.addLayout(view_layout)
        main_layout.addWidget(self.log_text)
        
        # Inicializar lista de portas
        self.refresh_ports()
        
    def refresh_ports(self):
        """Atualiza a lista de portas seriais disponíveis"""
        self.port_combo.clear()
        
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(port.device)
            
        if self.port_combo.count() == 0:
            self.log_message("Nenhuma porta serial encontrada")
            
    def toggle_monitoring(self):
        """Inicia ou para o monitoramento serial"""
        if self.monitor_thread and self.monitor_thread.running:
            self.stop_monitoring()
            self.start_button.setText("Iniciar Monitoramento")
        else:
            self.start_monitoring()
            self.start_button.setText("Parar Monitoramento")
            
    def start_monitoring(self):
        """Inicia o monitoramento serial"""
        if self.port_combo.count() == 0:
            self.log_message("Nenhuma porta serial disponível")
            return
            
        port = self.port_combo.currentText()
        baud_rate = int(self.baud_combo.currentText())
        
        self.log_message(f"Iniciando monitoramento na porta: {port} ({baud_rate} baud)")
        
        # Parar thread anterior se existir
        if self.monitor_thread:
            self.monitor_thread.stop()
            
        # Iniciar nova thread
        self.monitor_thread = SerialMonitorThread(port, baud_rate)
        self.monitor_thread.serial_data.connect(self.handle_serial_data)
        self.monitor_thread.serial_error.connect(self.handle_serial_error)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Para o monitoramento serial"""
        if self.monitor_thread:
            self.monitor_thread.stop()
            self.log_message("Monitoramento parado")
            
    def handle_serial_data(self, data):
        """Manipula dados recebidos da porta serial"""
        view_mode = self.view_combo.currentText()
        
        if view_mode == "Hexadecimal":
            hex_data = ' '.join([f"{b:02X}" for b in data])
            self.log_message(f"HEX: {hex_data}")
        elif view_mode == "ASCII":
            try:
                ascii_data = data.decode('ascii', errors='replace')
                self.log_message(f"ASCII: {ascii_data}")
            except Exception:
                self.log_message(f"ASCII (erro): {data}")
        elif view_mode == "Decimal":
            dec_data = ' '.join([str(b) for b in data])
            self.log_message(f"DEC: {dec_data}")
        elif view_mode == "MIDI":
            self.parse_midi_data(data)
            
    def parse_midi_data(self, data):
        """Analisa dados como mensagens MIDI"""
        i = 0
        while i < len(data):
            # Verifica se é um byte de status MIDI
            if data[i] & 0x80:  # Bit mais significativo = 1
                status_byte = data[i]
                message_type = status_byte & 0xF0
                channel = status_byte & 0x0F
                
                # Note On/Off (precisa de 3 bytes)
                if message_type in [0x80, 0x90] and i + 2 < len(data):
                    note = data[i+1]
                    velocity = data[i+2]
                    msg_type = "Note On" if message_type == 0x90 and velocity > 0 else "Note Off"
                    self.log_message(f"MIDI: {msg_type} - Canal: {channel+1}, Nota: {note}, Velocidade: {velocity}")
                    i += 3
                # Control Change (precisa de 3 bytes)
                elif message_type == 0xB0 and i + 2 < len(data):
                    controller = data[i+1]
                    value = data[i+2]
                    self.log_message(f"MIDI: Control Change - Canal: {channel+1}, Controle: {controller}, Valor: {value}")
                    i += 3
                # Program Change (precisa de 2 bytes)
                elif message_type == 0xC0 and i + 1 < len(data):
                    program = data[i+1]
                    self.log_message(f"MIDI: Program Change - Canal: {channel+1}, Programa: {program}")
                    i += 2
                # SysEx (tamanho variável)
                elif status_byte == 0xF0:
                    # Procura pelo byte de fim de SysEx (0xF7)
                    end_index = i + 1
                    while end_index < len(data) and data[end_index] != 0xF7:
                        end_index += 1
                    
                    if end_index < len(data):
                        sysex_data = data[i+1:end_index]
                        hex_data = ' '.join([f"{b:02X}" for b in sysex_data])
                        self.log_message(f"MIDI: SysEx - Dados: {hex_data}")
                        i = end_index + 1
                    else:
                        self.log_message(f"MIDI: SysEx incompleto")
                        i += 1
                else:
                    self.log_message(f"MIDI: Status desconhecido: {status_byte:02X}")
                    i += 1
            else:
                # Dados sem byte de status (running status ou dados inválidos)
                self.log_message(f"MIDI: Dados sem status: {data[i]:02X}")
                i += 1
            
    def handle_serial_error(self, error_msg):
        """Manipula erros da porta serial"""
        self.log_message(f"ERRO: {error_msg}")
        self.stop_monitoring()
        self.start_button.setText("Iniciar Monitoramento")
            
    def log_message(self, message):
        """Adiciona uma mensagem ao log"""
        timestamp = time.strftime("%H:%M:%S.%f")[:-3]
        self.log_text.append(f"[{timestamp}] {message}")
        
    def clear_log(self):
        """Limpa o log"""
        self.log_text.clear()
        
    def closeEvent(self, event):
        """Manipula o evento de fechamento da janela"""
        if self.monitor_thread:
            self.monitor_thread.stop()
        event.accept()

def main():
    """Função principal"""
    app = QApplication(sys.argv)
    window = SerialMonitorWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()