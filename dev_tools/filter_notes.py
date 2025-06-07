#!/usr/bin/env python3
"""
Filtro MIDI para MicroDrum - Filtra notas indesejadas
"""

import sys
import time
import rtmidi
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLabel, QTextEdit, QWidget, QCheckBox
from PyQt5.QtCore import QThread, pyqtSignal, Qt

class MidiFilterThread(QThread):
    """Thread para filtrar mensagens MIDI indesejadas"""
    log_message = pyqtSignal(str)
    
    def __init__(self, input_port, output_port, filtered_notes):
        super().__init__()
        self.input_port = input_port
        self.output_port = output_port
        self.filtered_notes = filtered_notes
        self.running = True
        
    def run(self):
        """Executa o filtro MIDI"""
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
        if len(message) >= 3:
            status_byte = message[0]
            note = message[1]
            velocity = message[2]
            
            # Verifica se é uma mensagem Note On
            if (status_byte & 0xF0) == 0x90:
                # Verifica se a nota está na lista de notas filtradas
                if note in self.filtered_notes:
                    self.log_message.emit(f"Nota filtrada: {note}")
                    return
                    
            # Passa a mensagem adiante
            midi_out.send_message(message)
            
            # Log da mensagem
            if (status_byte & 0xF0) == 0x90:
                self.log_message.emit(f"Note On: nota={note}, velocidade={velocity}")
            elif (status_byte & 0xF0) == 0x80:
                self.log_message.emit(f"Note Off: nota={note}, velocidade={velocity}")
        else:
            # Passa a mensagem adiante sem modificação
            midi_out.send_message(message)
            
    def stop(self):
        """Para a thread"""
        self.running = False
        self.wait()

class MidiFilterWindow(QMainWindow):
    """Interface para o filtro MIDI"""
    
    def __init__(self):
        super().__init__()
        self.filter_thread = None
        self.filtered_notes = [36]  # Filtrar a nota 36 (bumbo) por padrão
        self.initUI()
        
    def initUI(self):
        """Inicializa a interface"""
        self.setWindowTitle("Filtro MIDI para MicroDrum")
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
        
        # Opções de filtro
        filter_layout = QHBoxLayout()
        self.filter_kick = QCheckBox("Filtrar Bumbo (36)")
        self.filter_kick.setChecked(True)
        self.filter_kick.stateChanged.connect(self.update_filters)
        filter_layout.addWidget(self.filter_kick)
        
        # Botões
        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Atualizar")
        self.refresh_button.clicked.connect(self.refresh_ports)
        self.start_button = QPushButton("Iniciar")
        self.start_button.clicked.connect(self.toggle_filter)
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
        main_layout.addLayout(filter_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.log_text)
        
        # Inicializar portas
        self.refresh_ports()
        
        # Instruções
        self.log_message("=== Filtro MIDI para MicroDrum ===")
        self.log_message("Esta ferramenta filtra notas MIDI indesejadas do MicroDrum.")
        self.log_message("1. Selecione a porta de entrada (onde o MicroDrum está enviando)")
        self.log_message("2. Selecione a porta de saída (onde o Addictive Drums está recebendo)")
        self.log_message("3. Marque as notas que deseja filtrar")
        self.log_message("4. Clique em 'Iniciar'")
        
    def update_filters(self):
        """Atualiza a lista de notas filtradas"""
        self.filtered_notes = []
        if self.filter_kick.isChecked():
            self.filtered_notes.append(36)
        
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
            
    def toggle_filter(self):
        """Inicia ou para o filtro MIDI"""
        if self.filter_thread and self.filter_thread.running:
            self.stop_filter()
            self.start_button.setText("Iniciar")
        else:
            self.start_filter()
            self.start_button.setText("Parar")
            
    def start_filter(self):
        """Inicia o filtro MIDI"""
        try:
            input_idx = int(self.input_combo.currentText().split(":")[0])
            output_idx = int(self.output_combo.currentText().split(":")[0])
            
            if input_idx == output_idx:
                self.log_message("Erro: As portas de entrada e saída não podem ser as mesmas")
                return
                
            # Parar thread anterior se existir
            if self.filter_thread:
                self.filter_thread.stop()
                
            # Iniciar nova thread
            self.filter_thread = MidiFilterThread(input_idx, output_idx, self.filtered_notes)
            self.filter_thread.log_message.connect(self.log_message)
            self.filter_thread.start()
            
            self.log_message("Filtro MIDI iniciado")
            self.log_message(f"Notas filtradas: {self.filtered_notes}")
            
        except Exception as e:
            self.log_message(f"Erro ao iniciar: {str(e)}")
            
    def stop_filter(self):
        """Para o filtro MIDI"""
        if self.filter_thread:
            self.filter_thread.stop()
            self.log_message("Filtro MIDI parado")
            
    def log_message(self, message):
        """Adiciona uma mensagem ao log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
    def clear_log(self):
        """Limpa o log"""
        self.log_text.clear()
        
    def closeEvent(self, event):
        """Manipula o evento de fechamento da janela"""
        if self.filter_thread:
            self.filter_thread.stop()
        event.accept()

def main():
    """Função principal"""
    app = QApplication(sys.argv)
    window = MidiFilterWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()