#!/usr/bin/env python3
"""
MIDI Bridge para MicroDrum Config Tool - Intercepta e corrige mensagens MIDI
"""

import sys
import time
import rtmidi
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QComboBox, QPushButton, QLabel, QTextEdit, QWidget,
                            QCheckBox, QSpinBox)
from PyQt5.QtCore import QThread, pyqtSignal, Qt

class MidiBridgeThread(QThread):
    """Thread para interceptar e corrigir mensagens MIDI"""
    log_message = pyqtSignal(str)
    
    def __init__(self, input_port, output_port, note_map):
        super().__init__()
        self.input_port = input_port
        self.output_port = output_port
        self.note_map = note_map
        self.running = True
        
    def run(self):
        """Executa a ponte MIDI"""
        try:
            # Inicializar porta MIDI de entrada
            midi_in = rtmidi.MidiIn()
            if self.input_port < midi_in.get_port_count():
                midi_in.open_port(self.input_port)
                in_port_name = midi_in.get_port_name(self.input_port)
                self.log_message.emit(f"Porta MIDI de entrada {in_port_name} aberta")
            else:
                self.log_message.emit("Erro: Porta MIDI de entrada inválida")
                return
                
            # Inicializar porta MIDI de saída
            midi_out = rtmidi.MidiOut()
            if self.output_port < midi_out.get_port_count():
                midi_out.open_port(self.output_port)
                out_port_name = midi_out.get_port_name(self.output_port)
                self.log_message.emit(f"Porta MIDI de saída {out_port_name} aberta")
            else:
                self.log_message.emit("Erro: Porta MIDI de saída inválida")
                midi_in.close_port()
                return
            
            # Loop principal
            while self.running:
                msg = midi_in.get_message()
                if msg:
                    message, deltatime = msg
                    self.process_midi_message(message, midi_out)
                time.sleep(0.001)
                
            # Limpar
            midi_in.close_port()
            midi_out.close_port()
            self.log_message.emit("Bridge MIDI encerrada")
            
        except Exception as e:
            self.log_message.emit(f"Erro: {str(e)}")
            
    def process_midi_message(self, message, midi_out):
        """Processa e corrige mensagens MIDI"""
        if len(message) >= 3:
            status_byte = message[0]
            data1 = message[1]
            data2 = message[2]
            
            # Verifica se é uma mensagem Note On
            if (status_byte & 0xF0) == 0x90:
                # Mapeia a nota se estiver no mapeamento
                mapped_note = self.note_map.get(data1, data1)
                
                # Ajusta a velocidade se for muito baixa
                velocity = max(data2, 1) if data2 > 0 else 64
                
                # Cria uma mensagem Note On corrigida
                new_message = [status_byte, mapped_note, velocity]
                
                # Envia a mensagem corrigida
                midi_out.send_message(new_message)
                
                channel = (status_byte & 0x0F) + 1
                self.log_message.emit(f"Note On corrigido - Canal: {channel}, Nota: {data1}->{mapped_note}, Velocidade: {data2}->{velocity}")
            
            # Verifica se é uma mensagem Note Off
            elif (status_byte & 0xF0) == 0x80:
                # Mapeia a nota se estiver no mapeamento
                mapped_note = self.note_map.get(data1, data1)
                
                # Cria uma mensagem Note Off corrigida
                new_message = [status_byte, mapped_note, data2]
                
                # Envia a mensagem corrigida
                midi_out.send_message(new_message)
                
                channel = (status_byte & 0x0F) + 1
                self.log_message.emit(f"Note Off corrigido - Canal: {channel}, Nota: {data1}->{mapped_note}, Velocidade: {data2}")
            
            # Para outros tipos de mensagens, passa adiante sem modificação
            else:
                midi_out.send_message(message)
                self.log_message.emit(f"Mensagem passada adiante: {message}")
        else:
            # Mensagens curtas são passadas adiante sem modificação
            midi_out.send_message(message)
            self.log_message.emit(f"Mensagem curta passada adiante: {message}")
            
    def stop(self):
        """Para a bridge"""
        self.running = False
        self.wait()

class MidiBridgeWindow(QMainWindow):
    """Janela principal da bridge MIDI"""
    
    def __init__(self):
        super().__init__()
        self.bridge_thread = None
        self.note_map = {
            0: 38,   # Snare (nota padrão para snare no GM)
            1: 36,   # Kick (nota padrão para kick no GM)
            2: 42,   # Hi-Hat Fechado
            3: 46,   # Hi-Hat Aberto
            4: 41,   # Tom 1
            5: 43,   # Tom 2
            6: 45,   # Tom 3
            7: 49,   # Crash
            8: 51,   # Ride
        }
        self.initUI()
        
    def initUI(self):
        """Inicializa a interface do usuário"""
        self.setWindowTitle("MIDI Bridge para MicroDrum Config Tool")
        self.setGeometry(100, 100, 700, 500)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Área de configuração MIDI de entrada
        input_layout = QHBoxLayout()
        self.input_label = QLabel("MIDI de Entrada (do MicroDrum):")
        self.input_combo = QComboBox()
        
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_combo)
        
        # Área de configuração MIDI de saída
        output_layout = QHBoxLayout()
        self.output_label = QLabel("MIDI de Saída (para Addictive Drums):")
        self.output_combo = QComboBox()
        
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_combo)
        
        # Botões de controle
        control_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Atualizar Portas")
        self.refresh_button.clicked.connect(self.refresh_ports)
        self.start_button = QPushButton("Iniciar Bridge")
        self.start_button.clicked.connect(self.toggle_bridge)
        self.clear_button = QPushButton("Limpar Log")
        self.clear_button.clicked.connect(self.clear_log)
        
        control_layout.addWidget(self.refresh_button)
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.clear_button)
        
        # Área de log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QTextEdit.NoWrap)
        self.log_text.setStyleSheet("font-family: Menlo, Monaco, Courier, monospace;")
        
        # Adicionar layouts ao layout principal
        main_layout.addLayout(input_layout)
        main_layout.addLayout(output_layout)
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.log_text)
        
        # Inicializar listas de portas
        self.refresh_ports()
        
        # Instruções iniciais
        self.log_message("=== MIDI Bridge para MicroDrum Config Tool ===")
        self.log_message("Esta ferramenta corrige as mensagens MIDI enviadas pelo MicroDrum Config Tool.")
        self.log_message("Instruções:")
        self.log_message("1. Selecione a porta MIDI de entrada (onde o MicroDrum Config Tool está enviando)")
        self.log_message("2. Selecione a porta MIDI de saída (onde o Addictive Drums 2 está recebendo)")
        self.log_message("3. Clique em 'Iniciar Bridge'")
        self.log_message("4. Use o MicroDrum Config Tool normalmente")
        
    def refresh_ports(self):
        """Atualiza as listas de portas MIDI"""
        # Portas MIDI de entrada
        self.input_combo.clear()
        midi_in = rtmidi.MidiIn()
        in_ports = midi_in.get_ports()
        
        for i, port in enumerate(in_ports):
            self.input_combo.addItem(f"{i}: {port}")
            
            # Selecionar automaticamente porta IAC se disponível
            if "IAC" in port:
                self.input_combo.setCurrentIndex(i)
                
        if self.input_combo.count() == 0:
            self.log_message("Nenhuma porta MIDI de entrada encontrada")
            
        # Portas MIDI de saída
        self.output_combo.clear()
        midi_out = rtmidi.MidiOut()
        out_ports = midi_out.get_ports()
        
        for i, port in enumerate(out_ports):
            self.output_combo.addItem(f"{i}: {port}")
            
            # Selecionar automaticamente porta IAC se disponível
            if "IAC" in port and i != self.input_combo.currentIndex():
                self.output_combo.setCurrentIndex(i)
                
        if self.output_combo.count() == 0:
            self.log_message("Nenhuma porta MIDI de saída encontrada")
            
    def toggle_bridge(self):
        """Inicia ou para a bridge MIDI"""
        if self.bridge_thread and self.bridge_thread.running:
            self.stop_bridge()
            self.start_button.setText("Iniciar Bridge")
        else:
            self.start_bridge()
            self.start_button.setText("Parar Bridge")
            
    def start_bridge(self):
        """Inicia a bridge MIDI"""
        if self.input_combo.count() == 0 or self.output_combo.count() == 0:
            self.log_message("Erro: Portas MIDI não disponíveis")
            return
            
        # Extrair índices das portas MIDI
        input_text = self.input_combo.currentText()
        output_text = self.output_combo.currentText()
        
        try:
            input_port = int(input_text.split(":")[0])
            output_port = int(output_text.split(":")[0])
        except ValueError:
            self.log_message("Erro: Formato de porta MIDI inválido")
            return
            
        if input_port == output_port:
            self.log_message("Erro: As portas de entrada e saída não podem ser as mesmas")
            return
            
        self.log_message(f"Iniciando bridge: MIDI porta {input_port} -> MIDI porta {output_port}")
        self.log_message("Mapeamento de notas:")
        for orig, mapped in self.note_map.items():
            self.log_message(f"  Nota {orig} -> Nota {mapped}")
        
        # Parar thread anterior se existir
        if self.bridge_thread:
            self.bridge_thread.stop()
            
        # Iniciar nova thread
        self.bridge_thread = MidiBridgeThread(input_port, output_port, self.note_map)
        self.bridge_thread.log_message.connect(self.log_message)
        self.bridge_thread.start()
        
    def stop_bridge(self):
        """Para a bridge MIDI"""
        if self.bridge_thread:
            self.bridge_thread.stop()
            self.log_message("Bridge parada")
            
    def log_message(self, message):
        """Adiciona uma mensagem ao log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
    def clear_log(self):
        """Limpa o log"""
        self.log_text.clear()
        
    def closeEvent(self, event):
        """Manipula o evento de fechamento da janela"""
        if self.bridge_thread:
            self.bridge_thread.stop()
        event.accept()

def main():
    """Função principal"""
    app = QApplication(sys.argv)
    window = MidiBridgeWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()