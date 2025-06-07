#!/usr/bin/env python3
"""
Correção direta de MIDI para MicroDrum - Converte mensagens Program Change em Note On
"""

import sys
import time
import rtmidi
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLabel, QTextEdit, QWidget
from PyQt5.QtCore import QThread, pyqtSignal

class MidiFixThread(QThread):
    """Thread para corrigir mensagens MIDI"""
    log_message = pyqtSignal(str)
    
    def __init__(self, input_port, output_port):
        super().__init__()
        self.input_port = input_port
        self.output_port = output_port
        self.running = True
        self.buffer = []
        
    def run(self):
        """Executa a correção MIDI"""
        try:
            # Inicializar portas MIDI
            midi_in = rtmidi.MidiIn()
            midi_out = rtmidi.MidiOut()
            
            if self.input_port < midi_in.get_port_count() and self.output_port < midi_out.get_port_count():
                midi_in.open_port(self.input_port)
                midi_out.open_port(self.output_port)
                
                in_port_name = midi_in.get_port_name(self.input_port)
                out_port_name = midi_out.get_port_name(self.output_port)
                self.log_message.emit(f"Conectado: {in_port_name} -> {out_port_name}")
                
                # Loop principal
                while self.running:
                    msg = midi_in.get_message()
                    if msg:
                        message, deltatime = msg
                        self.process_message(message, midi_out)
                    time.sleep(0.001)
                    
                midi_in.close_port()
                midi_out.close_port()
            else:
                self.log_message.emit("Erro: Portas MIDI inválidas")
                
        except Exception as e:
            self.log_message.emit(f"Erro: {str(e)}")
            
    def process_message(self, message, midi_out):
        """Processa mensagens MIDI"""
        # Adiciona a mensagem ao buffer
        self.buffer.append(message)
        
        # Processa o buffer quando tiver mensagens suficientes
        if len(self.buffer) >= 3:
            # Verifica se temos um padrão de Program Change seguido por dois bytes
            if len(self.buffer[0]) == 2 and self.buffer[0][0] == 0xC0:
                # Extrai os dados
                note = self.buffer[1][0] if len(self.buffer[1]) > 0 else 0
                velocity = self.buffer[2][0] if len(self.buffer[2]) > 0 else 64
                
                # Mapeia a nota para o padrão GM
                note_map = {0: 38, 1: 36, 2: 42, 3: 46, 4: 41, 5: 43, 6: 45, 7: 49, 8: 51}
                mapped_note = note_map.get(note, note)
                
                # Garante velocidade não-zero
                if velocity == 0:
                    velocity = 64
                
                # Cria uma mensagem Note On no canal 10 (bateria)
                note_on = [0x99, mapped_note, velocity]
                
                # Envia a mensagem
                midi_out.send_message(note_on)
                self.log_message.emit(f"Convertido: PC+{note}+{velocity} -> Note On canal 10, nota {mapped_note}, velocidade {velocity}")
                
                # Limpa o buffer
                self.buffer = []
            else:
                # Se não for um padrão reconhecido, remove a mensagem mais antiga
                self.buffer.pop(0)
                
                # Passa a mensagem original adiante
                midi_out.send_message(message)
                self.log_message.emit(f"Passado adiante: {message}")
                
    def stop(self):
        """Para a thread"""
        self.running = False
        self.wait()

class MidiFixWindow(QMainWindow):
    """Interface para a correção MIDI"""
    
    def __init__(self):
        super().__init__()
        self.fix_thread = None
        self.initUI()
        
    def initUI(self):
        """Inicializa a interface"""
        self.setWindowTitle("Correção MIDI para MicroDrum")
        self.setGeometry(100, 100, 600, 400)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Seleção de portas MIDI
        input_layout = QHBoxLayout()
        self.input_label = QLabel("Entrada MIDI:")
        self.input_combo = QComboBox()
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_combo)
        
        output_layout = QHBoxLayout()
        self.output_label = QLabel("Saída MIDI:")
        self.output_combo = QComboBox()
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_combo)
        
        # Botões
        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Atualizar")
        self.refresh_button.clicked.connect(self.refresh_ports)
        self.start_button = QPushButton("Iniciar")
        self.start_button.clicked.connect(self.toggle_fix)
        self.clear_button = QPushButton("Limpar Log")
        self.clear_button.clicked.connect(self.clear_log)
        
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.clear_button)
        
        # Área de log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        
        # Adicionar layouts ao layout principal
        main_layout.addLayout(input_layout)
        main_layout.addLayout(output_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.log_text)
        
        # Inicializar portas
        self.refresh_ports()
        
        # Instruções
        self.log_message("=== Correção MIDI para MicroDrum ===")
        self.log_message("Esta ferramenta converte mensagens Program Change do MicroDrum em Note On para o Addictive Drums.")
        self.log_message("1. Selecione a porta de entrada (onde o MicroDrum está enviando)")
        self.log_message("2. Selecione a porta de saída (onde o Addictive Drums está recebendo)")
        self.log_message("3. Clique em 'Iniciar'")
        
    def refresh_ports(self):
        """Atualiza a lista de portas MIDI"""
        # Limpar combos
        self.input_combo.clear()
        self.output_combo.clear()
        
        # Listar portas de entrada
        midi_in = rtmidi.MidiIn()
        in_ports = midi_in.get_ports()
        for i, port in enumerate(in_ports):
            self.input_combo.addItem(f"{i}: {port}")
            if "IAC" in port:
                self.input_combo.setCurrentIndex(i)
                
        # Listar portas de saída
        midi_out = rtmidi.MidiOut()
        out_ports = midi_out.get_ports()
        for i, port in enumerate(out_ports):
            self.output_combo.addItem(f"{i}: {port}")
            if "IAC" in port and i != self.input_combo.currentIndex():
                self.output_combo.setCurrentIndex(i)
                
        if not in_ports:
            self.log_message("Nenhuma porta MIDI de entrada encontrada")
        if not out_ports:
            self.log_message("Nenhuma porta MIDI de saída encontrada")
            
    def toggle_fix(self):
        """Inicia ou para a correção MIDI"""
        if self.fix_thread and self.fix_thread.running:
            self.stop_fix()
            self.start_button.setText("Iniciar")
        else:
            self.start_fix()
            self.start_button.setText("Parar")
            
    def start_fix(self):
        """Inicia a correção MIDI"""
        try:
            input_idx = int(self.input_combo.currentText().split(":")[0])
            output_idx = int(self.output_combo.currentText().split(":")[0])
            
            if input_idx == output_idx:
                self.log_message("Erro: As portas de entrada e saída não podem ser as mesmas")
                return
                
            # Parar thread anterior se existir
            if self.fix_thread:
                self.fix_thread.stop()
                
            # Iniciar nova thread
            self.fix_thread = MidiFixThread(input_idx, output_idx)
            self.fix_thread.log_message.connect(self.log_message)
            self.fix_thread.start()
            
            self.log_message("Correção MIDI iniciada")
            
        except Exception as e:
            self.log_message(f"Erro ao iniciar: {str(e)}")
            
    def stop_fix(self):
        """Para a correção MIDI"""
        if self.fix_thread:
            self.fix_thread.stop()
            self.log_message("Correção MIDI parada")
            
    def log_message(self, message):
        """Adiciona uma mensagem ao log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
    def clear_log(self):
        """Limpa o log"""
        self.log_text.clear()
        
    def closeEvent(self, event):
        """Manipula o evento de fechamento da janela"""
        if self.fix_thread:
            self.fix_thread.stop()
        event.accept()

def main():
    """Função principal"""
    app = QApplication(sys.argv)
    window = MidiFixWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()