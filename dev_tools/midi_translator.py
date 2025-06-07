#!/usr/bin/env python3
"""
Tradutor MIDI para MicroDrum - Corrige mensagens MIDI malformadas
"""

import sys
import time
import serial
import serial.tools.list_ports
import rtmidi
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QComboBox, QPushButton, QLabel, QTextEdit, QWidget,
                            QCheckBox, QSpinBox)
from PyQt5.QtCore import QThread, pyqtSignal, Qt

class MidiTranslatorThread(QThread):
    """Thread para traduzir mensagens seriais em MIDI válido"""
    log_message = pyqtSignal(str)
    midi_message = pyqtSignal(list)
    
    def __init__(self, serial_port, baud_rate, midi_port):
        super().__init__()
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.midi_port = midi_port
        self.running = True
        self.buffer = bytearray()
        
    def run(self):
        """Executa a tradução MIDI"""
        try:
            # Inicializar porta serial
            ser = serial.Serial(self.serial_port, self.baud_rate, timeout=0.1)
            self.log_message.emit(f"Porta serial {self.serial_port} aberta")
            
            # Inicializar porta MIDI
            midi_out = rtmidi.MidiOut()
            if self.midi_port < midi_out.get_port_count():
                midi_out.open_port(self.midi_port)
                port_name = midi_out.get_port_name(self.midi_port)
                self.log_message.emit(f"Porta MIDI {port_name} aberta")
            else:
                self.log_message.emit("Erro: Porta MIDI inválida")
                ser.close()
                return
            
            # Loop principal
            while self.running:
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting)
                    self.buffer.extend(data)
                    self.process_buffer(midi_out)
                time.sleep(0.001)
                
            # Limpar
            ser.close()
            midi_out.close_port()
            self.log_message.emit("Tradutor MIDI encerrado")
            
        except Exception as e:
            self.log_message.emit(f"Erro: {str(e)}")
            
    def process_buffer(self, midi_out):
        """Processa o buffer de dados e extrai mensagens MIDI válidas"""
        # Procura por padrões conhecidos no buffer
        i = 0
        while i < len(self.buffer):
            # Verifica se temos dados suficientes para uma mensagem completa
            if i + 2 >= len(self.buffer):
                break
                
            # Verifica se é um padrão conhecido do MicroDrum
            if self.buffer[i] == 0xC0:  # Program Change (pode ser um marcador)
                # Verifica se os próximos bytes podem formar uma nota
                if i + 2 < len(self.buffer):
                    # Extrai os dados
                    data1 = self.buffer[i+1]
                    data2 = self.buffer[i+2]
                    
                    # Verifica se parece uma nota válida
                    if data1 <= 127 and data2 <= 127:
                        # Cria uma mensagem Note On no canal 10 (bateria)
                        midi_msg = [0x99, data1, data2]  # 0x99 = Note On canal 10
                        
                        # Envia a mensagem MIDI
                        midi_out.send_message(midi_msg)
                        self.midi_message.emit(midi_msg)
                        self.log_message.emit(f"Nota traduzida: {data1}, velocidade: {data2}")
                        
                        # Avança o buffer
                        i += 3
                        continue
            
            # Se não encontrou um padrão conhecido, avança um byte
            i += 1
            
        # Limpa o buffer processado
        if i > 0:
            self.buffer = self.buffer[i:]
            
    def stop(self):
        """Para o tradutor"""
        self.running = False
        self.wait()

class MidiTranslatorWindow(QMainWindow):
    """Janela principal do tradutor MIDI"""
    
    def __init__(self):
        super().__init__()
        self.translator_thread = None
        self.initUI()
        
    def initUI(self):
        """Inicializa a interface do usuário"""
        self.setWindowTitle("Tradutor MIDI para MicroDrum")
        self.setGeometry(100, 100, 700, 500)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Área de configuração serial
        serial_layout = QHBoxLayout()
        self.serial_label = QLabel("Porta Serial:")
        self.serial_combo = QComboBox()
        self.baud_label = QLabel("Baud Rate:")
        self.baud_combo = QComboBox()
        for baud in [9600, 19200, 31250, 38400, 57600, 115200]:
            self.baud_combo.addItem(str(baud))
        self.baud_combo.setCurrentText("115200")  # Padrão para MicroDrum
        
        serial_layout.addWidget(self.serial_label)
        serial_layout.addWidget(self.serial_combo)
        serial_layout.addWidget(self.baud_label)
        serial_layout.addWidget(self.baud_combo)
        
        # Área de configuração MIDI
        midi_layout = QHBoxLayout()
        self.midi_label = QLabel("Porta MIDI:")
        self.midi_combo = QComboBox()
        self.refresh_button = QPushButton("Atualizar")
        self.refresh_button.clicked.connect(self.refresh_ports)
        
        midi_layout.addWidget(self.midi_label)
        midi_layout.addWidget(self.midi_combo)
        midi_layout.addWidget(self.refresh_button)
        
        # Botões de controle
        control_layout = QHBoxLayout()
        self.start_button = QPushButton("Iniciar Tradutor")
        self.start_button.clicked.connect(self.toggle_translator)
        self.clear_button = QPushButton("Limpar Log")
        self.clear_button.clicked.connect(self.clear_log)
        
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.clear_button)
        
        # Área de log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QTextEdit.NoWrap)
        self.log_text.setStyleSheet("font-family: Menlo, Monaco, Courier, monospace;")
        
        # Adicionar layouts ao layout principal
        main_layout.addLayout(serial_layout)
        main_layout.addLayout(midi_layout)
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.log_text)
        
        # Inicializar listas de portas
        self.refresh_ports()
        
    def refresh_ports(self):
        """Atualiza as listas de portas seriais e MIDI"""
        # Portas seriais
        self.serial_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.serial_combo.addItem(port.device)
            
        if self.serial_combo.count() == 0:
            self.log_message("Nenhuma porta serial encontrada")
            
        # Portas MIDI
        self.midi_combo.clear()
        midi_out = rtmidi.MidiOut()
        ports = midi_out.get_ports()
        
        for i, port in enumerate(ports):
            self.midi_combo.addItem(f"{i}: {port}")
            
            # Selecionar automaticamente porta IAC se disponível
            if "IAC" in port:
                self.midi_combo.setCurrentIndex(i)
                
        if self.midi_combo.count() == 0:
            self.log_message("Nenhuma porta MIDI de saída encontrada")
            
    def toggle_translator(self):
        """Inicia ou para o tradutor MIDI"""
        if self.translator_thread and self.translator_thread.running:
            self.stop_translator()
            self.start_button.setText("Iniciar Tradutor")
        else:
            self.start_translator()
            self.start_button.setText("Parar Tradutor")
            
    def start_translator(self):
        """Inicia o tradutor MIDI"""
        if self.serial_combo.count() == 0 or self.midi_combo.count() == 0:
            self.log_message("Erro: Portas serial ou MIDI não disponíveis")
            return
            
        serial_port = self.serial_combo.currentText()
        baud_rate = int(self.baud_combo.currentText())
        
        # Extrair índice da porta MIDI do texto do combobox
        midi_text = self.midi_combo.currentText()
        try:
            midi_port = int(midi_text.split(":")[0])
        except ValueError:
            self.log_message("Erro: Formato de porta MIDI inválido")
            return
            
        self.log_message(f"Iniciando tradutor: {serial_port} -> MIDI porta {midi_port}")
        
        # Parar thread anterior se existir
        if self.translator_thread:
            self.translator_thread.stop()
            
        # Iniciar nova thread
        self.translator_thread = MidiTranslatorThread(serial_port, baud_rate, midi_port)
        self.translator_thread.log_message.connect(self.log_message)
        self.translator_thread.midi_message.connect(self.handle_midi_message)
        self.translator_thread.start()
        
    def stop_translator(self):
        """Para o tradutor MIDI"""
        if self.translator_thread:
            self.translator_thread.stop()
            self.log_message("Tradutor parado")
            
    def handle_midi_message(self, message):
        """Manipula mensagens MIDI traduzidas"""
        if len(message) >= 3:
            status_byte = message[0]
            data1 = message[1]
            data2 = message[2]
            
            if (status_byte & 0xF0) == 0x90:  # Note On
                channel = (status_byte & 0x0F) + 1
                self.log_message(f"MIDI enviado: Note On - Canal: {channel}, Nota: {data1}, Velocidade: {data2}")
            elif (status_byte & 0xF0) == 0x80:  # Note Off
                channel = (status_byte & 0x0F) + 1
                self.log_message(f"MIDI enviado: Note Off - Canal: {channel}, Nota: {data1}, Velocidade: {data2}")
            
    def log_message(self, message):
        """Adiciona uma mensagem ao log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
    def clear_log(self):
        """Limpa o log"""
        self.log_text.clear()
        
    def closeEvent(self, event):
        """Manipula o evento de fechamento da janela"""
        if self.translator_thread:
            self.translator_thread.stop()
        event.accept()

def main():
    """Função principal"""
    app = QApplication(sys.argv)
    window = MidiTranslatorWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()