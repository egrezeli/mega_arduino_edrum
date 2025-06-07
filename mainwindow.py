#!/usr/bin/env python3
#============================================================
#=>             pyMicroDrum v0.3.0
#=>             www.microdrum.net
#=>              CC BY-NC-SA 3.0
#=>
#=> Adaptado para Python 3 e PyQt5
#=============================================================

import serial
import time
import datetime
import _thread as thread
import struct
import sys
import os
import rtmidi
import serial.tools.list_ports
from PyQt5 import uic
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, Qt, QFile, QMetaType
from ctypes import *

# Importa o wrapper para rtmidi.MidiOut
try:
    from midi_wrapper import MidiOutWrapper
except ImportError:
    # Fallback caso o arquivo não exista
    class MidiOutWrapper:
        def __init__(self):
            self._midi_out = rtmidi.MidiOut()
            self.ports = self._get_ports_list()
        
        def _get_ports_list(self):
            ports = []
            count = self._midi_out.get_port_count()
            for i in range(count):
                ports.append(self._midi_out.get_port_name(i))
            return ports
        
        def get_ports(self):
            return self._get_ports_list()
        
        def get_port_count(self):
            return self._midi_out.get_port_count()
        
        def get_port_name(self, port):
            return self._midi_out.get_port_name(port)
        
        def send_message(self, message):
            self._midi_out.send_message(message)
        
        def open_port(self, port):
            self._midi_out.open_port(port)
        
        def close_port(self):
            self._midi_out.close_port()

# NOTA: As funcionalidades relacionadas ao FluidSynth não foram completamente testadas
# Tenta importar fluidsynth, mas trata possíveis erros
fluidsynth_available = False
try:
    import fluidsynth
    fluidsynth_available = True
except (ImportError, SyntaxError):
    # Se falhar, cria uma classe dummy para evitar erros
    class DummyFluidSynth:
        def __init__(self, *args, **kwargs):
            pass
        def start(self):
            pass
        def sfload(self, *args):
            return 0
        def program_select(self, *args):
            pass
        def noteon(self, *args):
            pass
        def delete(self):
            pass
    
    # Substitui o módulo fluidsynth pelo dummy
    import sys
    sys.modules['fluidsynth'] = type('fluidsynth', (), {'Synth': DummyFluidSynth})
    
# Registrar tipos personalizados para uso em sinais/slots entre threads
try:
    # Método alternativo para registrar QVector<int>
    from PyQt5.QtCore import QMetaType
    QMetaType.type("QVector<int>")
except Exception:
    # Se falhar, ignorar silenciosamente
    pass

( Ui_MainWindow, QMainWindow ) = uic.loadUiType( 'microdrum.ui' )

# Inicialização do MIDI
try:
    midi_out = MidiOutWrapper()
    if not midi_out.ports:
        print("Nenhuma porta MIDI encontrada. Verificando dispositivos virtuais...")
        # Tenta encontrar o IAC Driver
        midi_out_raw = rtmidi.MidiOut()
        for i in range(midi_out_raw.get_port_count()):
            port_name = midi_out_raw.get_port_name(i)
            if "IAC" in port_name:
                print(f"Dispositivo MIDI virtual encontrado: {port_name}")
                midi_out.ports = [port_name]
                break
except Exception as e:
    print("Erro ao inicializar MIDI:", e)
    # Fallback para caso nenhuma implementação funcione
    class DummyMidiOut:
        def __init__(self):
            self.ports = []
        def send_message(self, msg):
            print("MIDI message:", msg)
        def close_port(self):
            pass
        def open_port(self, port):
            pass
    midi_out = DummyMidiOut()

#serialSpeed=31250
# Velocidade da porta serial
serialSpeed=115200

# NOTA: Inicialização do FluidSynth - funcionalidade não foi completamente testada
if fluidsynth_available:
    fs = fluidsynth.Synth()
    fs.start()
    sfid = fs.sfload("example.sf2")  # Arquivo de exemplo pode não existir
    fs.program_select(0, sfid, 0, 0)


class PIN(Structure):
    _fields_ = [("name", c_char*20),("type", c_int),("note", c_int),("thresold", c_int),("scantime", c_int),("masktime", c_int),("retrigger", c_int),
                ("gain", c_int),("curve", c_int),("curveform", c_int),("xtalk", c_int),("xtalkgroup", c_int),("channel", c_int)]

pinArray=PIN*48
noteArray="C","C#","D","D#","E","F","F#","G","G#","A","A#","B"

Permutation = [ 0x72, 0x32, 0x25, 0x64, 0x64, 0x4f, 0x1e, 0x26, 0x2a, 0x74, 0x37, 0x09, 0x57, 0x02, 0x28,
            0x08, 0x14, 0x23, 0x49, 0x10, 0x62, 0x02, 0x1e, 0x7e, 0x5d, 0x1b, 0x27, 0x76, 0x7a, 0x76, 0x05, 0x2e ]


class MainWindow ( QMainWindow ):
    """MainWindow inherits QMainWindow"""
    ser=serial.Serial()
    
    pins=pinArray()
    pinType=dict()

    pbPinArray=[]

    # Usar sinais com tipos básicos para evitar problemas de compatibilidade
    updateMonitor = pyqtSignal(int,int,int)  # cmd, note, velocity
    logMessage = pyqtSignal(str)
    
    # Desabilitar mensagens de aviso do Qt
    @staticmethod
    def registerTypes():
        try:
            from PyQt5.QtCore import qInstallMessageHandler
            
            # Função que ignora mensagens de aviso
            def messageHandler(msg_type, context, msg):
                pass
                
            # Instalar o handler que ignora mensagens
            qInstallMessageHandler(messageHandler)
        except Exception:
            pass
    
    @staticmethod
    def register_meta_types():
        # Método mantido para compatibilidade
        MainWindow.registerTypes()
    
    def __init__ ( self, parent = None ):
        # Registrar tipos personalizados antes de inicializar a UI
        MainWindow.registerTypes()
        
        QMainWindow.__init__( self, parent )
        self.ui = Ui_MainWindow()
        self.ui.setupUi( self )
        
        # Adiciona o botão para desabilitar todos os pinos
        self.addDisableAllButton()
        
        # Adiciona informações sobre funcionalidades não testadas
        self.ui.rbFluidsynth.setText("To FluidSynth (não testado)")
        self.ui.rbSFZ.setText("To SFZ (não testado)")
        self.ui.rbSFZ.setEnabled(False)  # Desabilita a opção SFZ que não foi implementada
        
        # Corrigir o botão de atualizar MIDI
        self.ui.tbReloadmidi.setText("↻")
        
        # Inicializar a variável thread_running
        self.thread_running = False
        
        # Flag para controlar se já carregou configurações do Arduino
        self.configs_loaded_from_arduino = False
        
        # Adicionar tooltips aos botões principais
        self.ui.pbUploadAll.setToolTip("↑ Solicita todos os parâmetros do pin selecionado do Arduino (receber do Arduino)")
        self.ui.pbDownloadAll.setToolTip("↓ Envia todos os parâmetros do pin selecionado para o Arduino (enviar ao Arduino)")
        
        # Aumentar o tamanho dos botões de upload/download para mostrar as setas
        for btn in [self.ui.pbUploadType, self.ui.pbDownloadType, 
                   self.ui.pbUploadNote, self.ui.pbDownloadNote,
                   self.ui.pbUploadThresold, self.ui.pbDownloadThresold,
                   self.ui.pbUploadScantime, self.ui.pbDownloadScantime,
                   self.ui.pbUploadMasktime, self.ui.pbDownloadMasktime,
                   self.ui.pbUploadRetrigger, self.ui.pbDownloadRetrigger,
                   self.ui.pbUploadCurve, self.ui.pbDownloadCurve,
                   self.ui.pbUploadCurveform, self.ui.pbDownloadCurveform,
                   self.ui.pbUploadXtalk, self.ui.pbDownloadXtalk,
                   self.ui.pbUploadXtalkgroup, self.ui.pbDownloadXtalkgroup,
                   self.ui.pbUploadChannel, self.ui.pbDownloadChannel,
                   self.ui.pbUploadGain, self.ui.pbDownloadGain]:
            btn.setMinimumSize(30, 30)  # Aumenta o tamanho mínimo dos botões
            btn.setMaximumSize(30, 30)  # Mantém o tamanho máximo consistente
            
        # Adicionar tooltips detalhados a todos os botões
        self.add_button_tooltips()
        
        # Adicionar estilo visual para indicar status de conexão
        self.ui.ckSerialEnable.setStyleSheet("QCheckBox:checked { color: green; font-weight: bold; }")
        self.ui.cbSerial.setToolTip("Selecione a porta serial do Arduino Mega")
        self.ui.cbMIDI.setToolTip("Selecione a porta MIDI de saída")
        
        # Inicialmente desabilitar os botões de envio de parâmetros até que uma porta serial seja conectada
        self.update_button_states(False)
        
        # Definir o título inicial da janela
        self.setWindowTitle("Mega Arduino eDrum - Desconectado")
    
        self.pinType[0]="Piezo"
        self.pinType[1]="Switch"
        self.pinType[2]="HHC"
        self.pinType[15]="Disabled"  # Adicionar tipo 15
        self.pinType[127]="Disabled"

        self.pbPinArray=self.ui.pbPin0,self.ui.pbPin1,self.ui.pbPin2,self.ui.pbPin3,self.ui.pbPin4,self.ui.pbPin5,self.ui.pbPin6,self.ui.pbPin7,\
        self.ui.pbPin0_2,self.ui.pbPin1_2,self.ui.pbPin2_2,self.ui.pbPin3_2,self.ui.pbPin4_2,self.ui.pbPin5_2,self.ui.pbPin6_2,self.ui.pbPin7_2,\
        self.ui.pbPin0_3,self.ui.pbPin1_3,self.ui.pbPin2_3,self.ui.pbPin3_3,self.ui.pbPin4_3,self.ui.pbPin5_3,self.ui.pbPin6_3,self.ui.pbPin7_3,\
        self.ui.pbPin0_4,self.ui.pbPin1_4,self.ui.pbPin2_4,self.ui.pbPin3_4,self.ui.pbPin4_4,self.ui.pbPin5_4,self.ui.pbPin6_4,self.ui.pbPin7_4,\
        self.ui.pbPin0_5,self.ui.pbPin1_5,self.ui.pbPin2_5,self.ui.pbPin3_5,self.ui.pbPin4_5,self.ui.pbPin5_5,self.ui.pbPin6_5,self.ui.pbPin7_5,\
        self.ui.pbPin0_6,self.ui.pbPin1_6,self.ui.pbPin2_6,self.ui.pbPin3_6,self.ui.pbPin4_6,self.ui.pbPin5_6,self.ui.pbPin6_6,self.ui.pbPin7_6
        
        # Configurar o log na aba Tool
        self.ui.logOutput = QtWidgets.QTextEdit(self.ui.tab_2)
        self.ui.logOutput.setGeometry(10, 10, 760, 410)
        self.ui.logOutput.setReadOnly(True)
        self.ui.logOutput.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.ui.logOutput.setStyleSheet("font-family: Menlo, Monaco, Courier, monospace;")
        self.logMessage.connect(self.handle_logMessage)
        
        # Configurar a aba About
        self.setup_about_tab()
        
        # Carregar configurações do arquivo pins.ini como fallback
        self.load_pins_from_file()
    
        self.updateList()
    
        for note in range(100):
            self.ui.cbNote.addItem(self.getNoteString(note))

        self.updateMonitor.connect(self.handle_updateMonitor)
            
        #MIDI OUT
        for port_name in midi_out.ports:
            self.ui.cbMIDI.addItem(port_name)

        #Serial
        serialports=serial.tools.list_ports.comports()
        for port in serialports:
            self.ui.cbSerial.addItem(port[0])

        self.ui.tPinList.setCurrentCell(0,0)
        
        # Log de inicialização
        self.log("Mega Arduino eDrum inicializado")
        
    def __del__ ( self ):
        # Sinaliza para o thread parar
        if hasattr(self, 'thread_running'):
            self.thread_running = False
            time.sleep(1.0)  # Dá mais tempo para o thread terminar
        
        # Fecha a porta serial se estiver aberta
        if hasattr(self, 'ser') and hasattr(self.ser, 'isOpen') and self.ser.isOpen():
            try:
                self.ser.close()
                print("Porta serial fechada durante destruição do objeto")
            except Exception as e:
                print(f"Erro ao fechar porta serial: {e}")
        
        # Limpa recursos
        if hasattr(self, 'ui'):
            self.ui = None
        if fluidsynth_available:    
            fs.delete()
        
    def closeEvent(self, event):
        # Sinaliza para o thread parar
        self.thread_running = False
        
        # Espera o thread terminar
        time.sleep(1.0)
        
        # Salva as configurações
        self.save_pins_to_file()
            
        # Fecha a porta serial se estiver aberta
        if hasattr(self, 'ser') and self.ser.isOpen():
            try:
                self.ser.close()
                self.log("Porta serial fechada durante encerramento")
            except Exception as e:
                print(f"Erro ao fechar porta serial: {e}")
            
    #------------------------------------------------------------------------------
    # UTILITY
    #------------------------------------------------------------------------------
                
    def load_pins_from_file(self):
        """Carrega as configurações do arquivo pins.ini"""
        try:
            f = open("pins.ini", "r")
            try:
                i=0
                for line in f:
                    data=line.rstrip().split(';')
                    self.pins[i].name=data[0].encode()
                    self.pins[i].type=int(data[1])
                    self.pins[i].note=int(data[2])
                    self.pins[i].thresold=int(data[3])
                    self.pins[i].scantime=int(data[4])
                    self.pins[i].masktime=int(data[5])
                    self.pins[i].retrigger=int(data[6])
                    self.pins[i].gain=int(data[7])
                    self.pins[i].curve=int(data[8])
                    self.pins[i].curveform=int(data[9])
                    self.pins[i].xtalk=int(data[10])
                    self.pins[i].xtalkgroup=int(data[11])
                    self.pins[i].channel=int(data[12])
                    i=i+1
                self.log("Configurações carregadas do arquivo pins.ini")
                # Atualiza a interface com as configurações carregadas
                self.updateList()
                # Seleciona o primeiro item da lista para mostrar os detalhes
                self.ui.tPinList.setCurrentCell(0, 0)
                self.selectPin()
            finally:
                f.close()
        except IOError:
            self.log("Arquivo pins.ini não encontrado. Usando configurações padrão.")
    
    def save_pins_to_file(self):
        """Salva as configurações atuais no arquivo pins.ini"""
        try:
            f = open("pins.ini", "w")
            try:
                for pin in self.pins:
                    f.write(pin.name.decode()+';'+str(pin.type)+';'+str(pin.note)+';'+str(pin.thresold)+';'+str(pin.scantime)+';'+str(pin.masktime)+';'+str(pin.retrigger)+';'+str(pin.gain)+';'+str(pin.curve)+';'+str(pin.curveform)+';'+str(pin.xtalk)+';'+str(pin.xtalkgroup)+';'+str(pin.channel)+'\n')
                self.log("Configurações salvas no arquivo pins.ini")
            finally:
                f.close()
        except Exception as e:
            self.log(f"Erro ao salvar configurações: {e}")
    def enableSerial(self, bool):
        """Habilita ou desabilita a conexão serial com o Arduino"""
        # Primeiro, garantir que o thread seja parado se estiver desabilitando
        if not bool:
            # Desativa o thread antes de qualquer operação
            self.thread_running = False
            time.sleep(1.0)  # Dá mais tempo para o thread terminar completamente
        
        if bool:
            port=str(self.ui.cbSerial.currentText())
            try:
                # Configura a porta serial com parâmetros otimizados para baixa latência
                self.ser = serial.Serial(
                    port=port,
                    baudrate=serialSpeed,
                    bytesize=8,
                    parity="N",
                    stopbits=1,
                    timeout=0.001,  # Timeout baixo para leitura responsiva
                    write_timeout=0.1,  # Timeout de escrita para evitar bloqueios
                    inter_byte_timeout=None,  # Sem timeout entre bytes para leitura contínua
                    exclusive=True  # Acesso exclusivo à porta para melhor performance
                )
                
                # Configura o tamanho do buffer se disponível
                if hasattr(self.ser, 'set_buffer_size'):
                    try:
                        self.ser.set_buffer_size(rx_size=4096, tx_size=4096)
                    except:
                        pass
                
                # Inicia o thread somente após abrir a porta serial
                self.thread_running = True
                thread.start_new_thread(self.read_midi, ("MIDI_Thread", 0.001, ))  # Reduz o delay do thread
                self.log(f"Porta serial {port} aberta com sucesso")
                
                # Aguarda estabilização da conexão
                time.sleep(1.0)
                
                # Mostra mensagem informando que está carregando configurações
                self.log("Carregando configurações do Arduino...")
                
                # Solicita configurações do Arduino
                self.request_all_arduino_configs()
                
                # Habilita os botões de envio de parâmetros
                self.update_button_states(True)
                # Atualiza o estilo visual para indicar conexão bem-sucedida
                self.ui.ckSerialEnable.setStyleSheet("QCheckBox:checked { color: green; font-weight: bold; }")
                # Atualiza o título da janela para indicar conexão
                self.setWindowTitle(f"Mega Arduino eDrum - Conectado a {port}")
            except Exception as e:
                self.log(f"Erro ao abrir porta serial {port}: {e}")
                # Desabilita os botões em caso de erro
                self.update_button_states(False)
                # Desmarca o checkbox sem chamar este método novamente
                self.ui.ckSerialEnable.blockSignals(True)
                self.ui.ckSerialEnable.setChecked(False)
                self.ui.ckSerialEnable.blockSignals(False)
                self.setWindowTitle("Mega Arduino eDrum - Desconectado")
        else:
            # A porta já foi fechada no início do método
            if hasattr(self, 'ser') and self.ser.isOpen():
                try:
                    self.ser.close()
                    self.log("Porta serial fechada")
                except Exception as e:
                    self.log(f"Erro ao fechar porta serial: {e}")
            # Desabilita os botões quando a porta é fechada
            self.update_button_states(False)
            self.setWindowTitle("Mega Arduino eDrum - Desconectado")
    def request_all_arduino_configs(self):
        """Solicita todas as configurações do Arduino"""
        if not hasattr(self, 'ser') or not self.ser.isOpen():
            self.log("Porta serial não está aberta. Impossível solicitar configurações.")
            return False
            
        self.log("Solicitando todas as configurações do Arduino...")
        
        # Limpa o flag de configurações carregadas
        self.configs_loaded_from_arduino = False
        
        # Solicita configurações para cada pin (0-47)
        for pin_num in range(48):
            data = 0xF0,0x77,0x02,pin_num,0x7F,0x00,0xF7
            txData = struct.pack("B"*len(data), *data)
            self.ser.write(txData)
            time.sleep(0.1)  # Pequeno delay entre solicitações
            
            # Processa eventos para manter a interface responsiva
            QtWidgets.QApplication.processEvents()
            
        self.log("Solicitação de configurações enviada. Aguardando resposta...")
        return True
    def read_midi(self, threadName, delay):
        # Thread_running já é inicializado no __init__
            
        self.log(f"Thread MIDI iniciado")
        
        # Variável local para controle do loop
        local_thread_running = True
        
        # Contador para verificar se recebemos configurações do Arduino
        params_received = 0
        
        # Aumenta a prioridade do thread para reduzir latência
        try:
            import os
            if hasattr(os, "nice"):  # Unix/Linux/macOS
                os.nice(-10)  # Aumenta a prioridade (valores menores = maior prioridade)
            elif os.name == 'nt':  # Windows
                try:
                    import psutil
                    p = psutil.Process()
                    p.nice(psutil.HIGH_PRIORITY_CLASS)
                except ImportError:
                    pass  # psutil não está disponível
        except Exception:
            pass  # Ignora erros ao tentar ajustar a prioridade
            
        # Configura o timeout da porta serial para ser mais responsivo
        if hasattr(self, 'ser') and self.ser.isOpen():
            self.ser.timeout = 0.001  # Timeout muito baixo para leitura mais frequente
            
        # Registrar QVector<int> neste thread também
        MainWindow.registerTypes()
            
        while local_thread_running:
            try:
                # Verifica se o thread deve continuar rodando
                local_thread_running = self.thread_running
                
                # Se o thread não deve mais rodar, sai do loop
                if not local_thread_running:
                    break
                    
                if hasattr(self, 'ser') and self.ser.isOpen():
                    try:
                        # Usa timeout muito baixo para reduzir latência
                        self.ser.timeout = 0.001  # Timeout menor para leitura mais responsiva
                        rxData = self.ser.read(1)
                        if len(rxData) <= 0:
                            # Reduz o tempo de espera para melhorar a responsividade
                            time.sleep(0.001)
                            continue
                    except (serial.SerialException, OSError):
                        # Se ocorrer erro na leitura, verifica se a porta ainda está aberta
                        if not self.thread_running or not hasattr(self, 'ser') or not self.ser.isOpen():
                            break
                        time.sleep(delay)
                        continue
                        
                    try:
                        cmd=rxData[0]
                        if cmd==0xF0:  # Em Python 3, bytes são números, não caracteres
                            try:
                                # Usa timeout muito baixo para reduzir latência
                                self.ser.timeout = 0.001  # Timeout menor para leitura mais responsiva
                                rxData = self.ser.read(6)
                                if len(rxData) < 6:
                                    continue
                                    
                                # Usar list() para evitar problemas com QVector<int>
                                data = list(struct.unpack("B"*len(rxData), rxData))
                                if data[1]==0x02: #ASKPARAM
                                    param_name = ""
                                    if data[3]==0x0D: #TYPE
                                        self.pins[data[2]].type=data[4]
                                        param_name = "TYPE"
                                    if data[3]==0x00: #NOTE
                                        self.pins[data[2]].note=data[4]
                                        param_name = "NOTE"
                                    if data[3]==0x01: #THRESOLD
                                        self.pins[data[2]].thresold=data[4]
                                        param_name = "THRESOLD"
                                    if data[3]==0x02: #SCANTIME
                                        self.pins[data[2]].scantime=data[4]
                                        param_name = "SCANTIME"
                                    if data[3]==0x03: #MASKTIME
                                        self.pins[data[2]].masktime=data[4]
                                        param_name = "MASKTIME"
                                    if data[3]==0x04: #RETRIGGER
                                        self.pins[data[2]].retrigger=data[4]
                                        param_name = "RETRIGGER"
                                    if data[3]==0x05: #CURVE
                                        self.pins[data[2]].curve=data[4]
                                        param_name = "CURVE"
                                    if data[3]==0x06: #XTALK
                                        self.pins[data[2]].xtalk=data[4]
                                        param_name = "XTALK"
                                    if data[3]==0x07: #XTALKGROUP
                                        self.pins[data[2]].xtalkgroup=data[4]
                                        param_name = "XTALKGROUP"
                                    if data[3]==0x08: #CURVEFORM
                                        self.pins[data[2]].curveform=data[4]
                                        param_name = "CURVEFORM"
                                    if data[3]==0x09: #GAIN
                                        self.pins[data[2]].gain=data[4]
                                        param_name = "GAIN"
                                    if data[3]==0x0E: #CHANNEL
                                        self.pins[data[2]].channel=data[4]
                                        param_name = "CHANNEL"
                                    
                                    # Incrementa o contador de parâmetros recebidos
                                    params_received += 1
                                    
                                    # Se recebemos muitos parâmetros, consideramos que as configurações foram carregadas
                                    if params_received >= 10 and not self.configs_loaded_from_arduino:
                                        self.configs_loaded_from_arduino = True
                                        self.log("Configurações carregadas do Arduino com sucesso")
                                        # Salva as configurações no arquivo pins.ini
                                        self.save_pins_to_file()
                                        # Seleciona o primeiro item da lista para mostrar os detalhes
                                        self.ui.tPinList.setCurrentCell(0, 0)
                                        self.selectPin()
                                    
                                    self.log(f"Parâmetro recebido: PIN {data[2]}, {param_name}={data[4]}")
                                    
                                    # Atualiza a lista de pins na interface
                                    self.updateList()
                                    
                                    # Se o pin atual é o que está sendo exibido, atualiza os controles da interface
                                    current_pin = self.ui.tPinList.currentRow()
                                    if current_pin == data[2]:
                                        self.selectPin()
                                        
                                    # Força a atualização visual da interface
                                    QtWidgets.QApplication.processEvents()
                                if data[1]==0x60:#License
                                    # Usar list() para evitar problemas com QVector<int>
                                    hash_value = self.getPearsonHash(list(data[2:4]))
                                    self.log(f"Solicitação de licença recebida: {data[2]},{data[3]} -> hash={hash_value}")
                                    dataSend = 0xF0,0x77,0x60,data[2],data[3],hash_value,0xF7
                                    txData = struct.pack("B"*len(dataSend), *dataSend)
                                    if hasattr(self, 'ser') and self.ser.isOpen():
                                        self.ser.write(txData)
                                        self.log("Resposta de licença enviada")
                            except Exception as e:
                                # Verifica se a porta ainda está aberta antes de logar o erro
                                if self.thread_running and hasattr(self, 'ser') and self.ser.isOpen():
                                    print(f"Erro ao processar comando SysEx: {e}")
                                continue
                        else:
                            try:
                                self.ser.timeout = 0.5  # Define um timeout para evitar bloqueio
                                rxData = self.ser.read(2)
                                if len(rxData) < 2:
                                    continue
                                    
                                # Em Python 3, bytes já são números, não precisamos de ord()
                                note = rxData[0]
                                vel = rxData[1]
                                # Prioriza o processamento de mensagens MIDI para reduzir latência
                                if self.ui.rbMIDI.isChecked():
                                    # Envia a mensagem MIDI imediatamente com alta prioridade
                                    try:
                                        # Envia a mensagem MIDI antes de qualquer outro processamento
                                        midi_out.send_message([cmd, note, vel]) # Note on
                                        
                                        # Força o processamento imediato (pode ajudar em alguns sistemas)
                                        if hasattr(midi_out, '_midi_out') and hasattr(midi_out._midi_out, '_rt_midi'):
                                            if hasattr(midi_out._midi_out._rt_midi, 'flush'):
                                                midi_out._midi_out._rt_midi.flush()
                                    except Exception as e:
                                        print(f"Erro ao enviar mensagem MIDI: {e}")
                                elif fluidsynth_available & self.ui.rbFluidsynth.isChecked():
                                    # NOTA: Funcionalidade FluidSynth não foi completamente testada
                                    fs.noteon(0, 60, 30)
                                elif self.ui.rbSFZ.isChecked():
                                    # NOTA: Funcionalidade SFZ não foi implementada/testada
                                    pass
                                
                                                # Emite o sinal para atualizar o monitor após o envio MIDI
                                # para não atrasar o processamento MIDI com atualizações de UI
                                QtWidgets.QApplication.processEvents()  # Processa eventos pendentes
                                
                                # Usar lista Python em vez de QVector<int>
                                cmd_val = int(cmd)
                                note_val = int(note)
                                vel_val = int(vel)
                                self.updateMonitor.emit(cmd_val, note_val, vel_val)
                            except Exception as e:
                                # Verifica se a porta ainda está aberta antes de logar o erro
                                if self.thread_running and hasattr(self, 'ser') and self.ser.isOpen():
                                    print(f"Erro ao processar mensagem MIDI: {e}")
                                continue
                    except (serial.SerialException, OSError):
                        # Se ocorrer erro durante o processamento, verifica se a porta ainda está aberta
                        if not self.thread_running or not hasattr(self, 'ser') or not self.ser.isOpen():
                            break
                        time.sleep(delay)
                        continue
                else:
                    time.sleep(delay)
            except Exception as e:
                # Verifica se o thread ainda deve estar rodando
                if not self.thread_running:
                    break
                time.sleep(delay)
        
        # Thread encerrado silenciosamente
    def update_button_states(self, enabled=False):
        """Atualiza o estado dos botões de envio de parâmetros com base na disponibilidade da porta serial"""
        # Lista de todos os botões que enviam comandos para o Arduino
        buttons = [
            self.ui.pbUploadAll, self.ui.pbDownloadAll,
            self.ui.pbUploadType, self.ui.pbDownloadType,
            self.ui.pbUploadNote, self.ui.pbDownloadNote,
            self.ui.pbUploadThresold, self.ui.pbDownloadThresold,
            self.ui.pbUploadScantime, self.ui.pbDownloadScantime,
            self.ui.pbUploadMasktime, self.ui.pbDownloadMasktime,
            self.ui.pbUploadRetrigger, self.ui.pbDownloadRetrigger,
            self.ui.pbUploadCurve, self.ui.pbDownloadCurve,
            self.ui.pbUploadCurveform, self.ui.pbDownloadCurveform,
            self.ui.pbUploadXtalk, self.ui.pbDownloadXtalk,
            self.ui.pbUploadXtalkgroup, self.ui.pbDownloadXtalkgroup,
            self.ui.pbUploadChannel, self.ui.pbDownloadChannel,
            self.ui.pbUploadGain, self.ui.pbDownloadGain
        ]
        
        # Atualiza o estado de cada botão
        for button in buttons:
            button.setEnabled(enabled)
            
        # Atualiza o estilo dos botões para indicar visualmente seu estado
        if not enabled:
            self.log("Botões de envio desabilitados - Conecte uma porta serial")
        else:
            self.log("Botões de envio habilitados - Porta serial conectada")
    def add_button_tooltips(self):
        """Adiciona tooltips explicativos aos botões e campos da interface"""
        # Botões principais - Explicação das setas
        self.ui.pbUploadType.setToolTip("↑ Solicitar tipo do Arduino (receber do Arduino)")
        self.ui.pbDownloadType.setToolTip("↓ Enviar tipo para o Arduino (enviar ao Arduino)")
        self.ui.pbUploadNote.setToolTip("↑ Solicitar nota MIDI do Arduino (receber do Arduino)")
        self.ui.pbDownloadNote.setToolTip("↓ Enviar nota MIDI para o Arduino (enviar ao Arduino)")
        self.ui.pbUploadThresold.setToolTip("↑ Solicitar threshold do Arduino (receber do Arduino)")
        self.ui.pbDownloadThresold.setToolTip("↓ Enviar threshold para o Arduino (enviar ao Arduino)")
        self.ui.pbUploadScantime.setToolTip("↑ Solicitar scantime do Arduino (receber do Arduino)")
        self.ui.pbDownloadScantime.setToolTip("↓ Enviar scantime para o Arduino (enviar ao Arduino)")
        self.ui.pbUploadMasktime.setToolTip("↑ Solicitar masktime do Arduino (receber do Arduino)")
        self.ui.pbDownloadMasktime.setToolTip("↓ Enviar masktime para o Arduino (enviar ao Arduino)")
        self.ui.pbUploadRetrigger.setToolTip("↑ Solicitar retrigger do Arduino (receber do Arduino)")
        self.ui.pbDownloadRetrigger.setToolTip("↓ Enviar retrigger para o Arduino (enviar ao Arduino)")
        self.ui.pbUploadCurve.setToolTip("↑ Solicitar curva do Arduino (receber do Arduino)")
        self.ui.pbDownloadCurve.setToolTip("↓ Enviar curva para o Arduino (enviar ao Arduino)")
        self.ui.pbUploadCurveform.setToolTip("↑ Solicitar forma da curva do Arduino (receber do Arduino)")
        self.ui.pbDownloadCurveform.setToolTip("↓ Enviar forma da curva para o Arduino (enviar ao Arduino)")
        self.ui.pbUploadXtalk.setToolTip("↑ Solicitar xtalk do Arduino (receber do Arduino)")
        self.ui.pbDownloadXtalk.setToolTip("↓ Enviar xtalk para o Arduino (enviar ao Arduino)")
        self.ui.pbUploadXtalkgroup.setToolTip("↑ Solicitar grupo xtalk do Arduino (receber do Arduino)")
        self.ui.pbDownloadXtalkgroup.setToolTip("↓ Enviar grupo xtalk para o Arduino (enviar ao Arduino)")
        self.ui.pbUploadChannel.setToolTip("↑ Solicitar canal do Arduino (receber do Arduino)")
        self.ui.pbDownloadChannel.setToolTip("↓ Enviar canal para o Arduino (enviar ao Arduino)")
        self.ui.pbUploadGain.setToolTip("↑ Solicitar ganho do Arduino (receber do Arduino)")
        self.ui.pbDownloadGain.setToolTip("↓ Enviar ganho para o Arduino (enviar ao Arduino)")
        
        # Checkbox
        self.ui.ckSave.setToolTip("Salvar configurações na EEPROM do Arduino")
        
        # Campos da aba configurations
        self.ui.lName.setToolTip("Nome do pad/trigger - Identificação do elemento da bateria")
        
        # Tipo de pad
        self.ui.cbType.setToolTip("Tipo de sensor: Piezo (para pads de bateria), Switch (para chimbais/pratos), HHC (para controle de chimbal), ou Disabled (desativado)")
        
        # Nota MIDI
        self.ui.cbNote.setToolTip("Nota MIDI que será enviada quando este pad for tocado - Define o som que será reproduzido")
        
        # Threshold
        self.ui.hsThresold.setToolTip("Limiar de sensibilidade - Valor mínimo para que o sinal seja reconhecido como uma batida (0-127)")
        self.ui.lThresold.setToolTip("Valor atual do limiar de sensibilidade (threshold)")
        
        # Scantime
        self.ui.hsScantime.setToolTip("Tempo de escaneamento - Duração em que o sistema busca o pico do sinal após detectar uma batida (0-127)")
        self.ui.lScantime.setToolTip("Valor atual do tempo de escaneamento (scantime)")
        
        # Masktime
        self.ui.hsMasktime.setToolTip("Tempo de máscara - Período em que novas batidas são ignoradas após uma detecção (0-127)")
        self.ui.lMasktime.setToolTip("Valor atual do tempo de máscara (masktime)")
        
        # Retrigger
        self.ui.hsRetrigger.setToolTip("Retrigger - Tempo mínimo entre batidas consecutivas no mesmo pad (0-127)")
        self.ui.lRetrigger.setToolTip("Valor atual do retrigger")
        
        # Gain
        self.ui.hsGain.setToolTip("Ganho - Amplificação do sinal do sensor (0-127)")
        self.ui.lGain.setToolTip("Valor atual do ganho")
        
        # Curve
        self.ui.cbCurve.setToolTip("Curva de velocidade - Define como a força da batida é convertida em velocidade MIDI")
        
        # Curveform
        self.ui.hsCurveform.setToolTip("Forma da curva - Ajusta a resposta da curva de velocidade selecionada (0-127)")
        self.ui.lCurveform.setToolTip("Valor atual da forma da curva")
        
        # Xtalk
        self.ui.hsXtalk.setToolTip("Cross-talk - Redução de interferência entre pads próximos (0-127)")
        self.ui.lXtalk.setToolTip("Valor atual do cross-talk")
        
        # Xtalkgroup
        self.ui.spXtalkgroup.setToolTip("Grupo de cross-talk - Pads no mesmo grupo são afetados pela configuração de cross-talk")
        
        # Channel
        self.ui.spChannel.setToolTip("Canal MIDI - Canal em que as mensagens MIDI deste pad serão enviadas (0-15)")
        
        # Botões principais
        self.ui.pbUploadAll.setToolTip("↑ Solicita todos os parâmetros do pin selecionado do Arduino (receber do Arduino)")
        self.ui.pbDownloadAll.setToolTip("↓ Envia todos os parâmetros do pin selecionado para o Arduino (enviar ao Arduino)")
    def setup_about_tab(self):
        """Configura a aba About com informações sobre o software"""
        # Remover qualquer layout existente
        if self.ui.tab_4.layout():
            old_layout = self.ui.tab_4.layout()
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            QtWidgets.QWidget().setLayout(old_layout)
        
        # Criar novo layout
        about_layout = QtWidgets.QVBoxLayout(self.ui.tab_4)
        about_layout.setContentsMargins(10, 10, 10, 10)
        about_layout.setSpacing(10)
        
        # Área de rolagem para garantir que todo o conteúdo seja visível
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        
        scroll_content = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        scroll_layout.setSpacing(15)
        
        # Logo simples
        logo_label = QtWidgets.QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        logo_path = "logo.png"
        if os.path.exists(logo_path):
            pixmap = QtGui.QPixmap(logo_path)
            # Tamanho menor e seguro
            logo_label.setPixmap(pixmap.scaled(150, 75, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # Fallback para texto
            logo_label.setText("Mega Arduino eDrum")
            logo_label.setStyleSheet("font-size: 24pt; font-weight: bold;")
        
        # Versão
        version_label = QtWidgets.QLabel("Versão 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("font-size: 14pt;")
        
        # Descrição
        description = QtWidgets.QLabel(
            "Mega Arduino eDrum é uma interface para configuração e uso de baterias eletrônicas " 
            "baseadas em Arduino Mega, permitindo a configuração de pads e o roteamento de sinais MIDI."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet("margin: 20px; font-size: 12pt;")
        
        # Informações de copyright e fork
        copyright_text = (
            "<p>Este programa é um fork do software original criado por Massimo Bernava.</p>"
            "<p>Foi reescrito para ser compatível com Python 3 e PyQt5, e para executar em ambientes Linux-like.</p>"
            "<p>Licença: CC BY-NC-SA 3.0</p>"
        )
        copyright_label = QtWidgets.QLabel(copyright_text)
        copyright_label.setWordWrap(True)
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("margin: 10px;")
        
        # Autor e contato
        author_text = (
            "<p><b>Desenvolvido por:</b> Evan Grezeli</p>"
            "<p><b>Contato:</b> <a href='mailto:egrezeli@gmail.com'>egrezeli@gmail.com</a></p>"
            "<p><b>Original por:</b> Massimo Bernava</p>"
        )
        author_label = QtWidgets.QLabel(author_text)
        author_label.setOpenExternalLinks(True)
        author_label.setAlignment(Qt.AlignCenter)
        author_label.setStyleSheet("margin: 10px;")
        
        # Adiciona widgets ao layout de rolagem
        scroll_layout.addWidget(logo_label)
        scroll_layout.addWidget(version_label)
        scroll_layout.addWidget(description)
        scroll_layout.addWidget(copyright_label)
        scroll_layout.addWidget(author_label)
        scroll_layout.addStretch(1)  # Espaço flexível no final
        
        # Configura a área de rolagem
        scroll_area.setWidget(scroll_content)
        
        # Adiciona a área de rolagem ao layout principal
        about_layout.addWidget(scroll_area)
    def handle_logMessage(self, message):
        """Manipula mensagens de log e as exibe no widget de log"""
        self.ui.logOutput.append(message)
        # Rola para o final do log
        scrollbar = self.ui.logOutput.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def log(self, message):
        """Adiciona uma mensagem ao log com timestamp"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_message = f"[{timestamp}] {message}"
        self.logMessage.emit(log_message)
                    
    def updateList(self):
        """Atualiza a lista de pins na interface"""
        # Salva a seleção atual
        current_row = self.ui.tPinList.currentRow()
        current_col = self.ui.tPinList.currentColumn()
        
        # Bloqueia sinais para evitar chamadas recursivas durante a atualização
        self.ui.tPinList.blockSignals(True)
        
        try:
            i=0
            for pin in self.pins:
                # Atualiza os itens da tabela
                self.ui.tPinList.setItem(i,0,QtWidgets.QTableWidgetItem(pin.name.decode()))
                # Usar get() para lidar com tipos desconhecidos
                type_name = self.pinType.get(pin.type, f"Tipo {pin.type}")
                self.ui.tPinList.setItem(i,1,QtWidgets.QTableWidgetItem(type_name))
                self.ui.tPinList.setItem(i,2,QtWidgets.QTableWidgetItem(self.getNoteString(pin.note)))
                self.ui.tPinList.setItem(i,3,QtWidgets.QTableWidgetItem(str(pin.thresold)))
                self.ui.tPinList.setItem(i,4,QtWidgets.QTableWidgetItem(str(pin.scantime)))
                self.ui.tPinList.setItem(i,5,QtWidgets.QTableWidgetItem(str(pin.masktime)))
                i=i+1
                
            # Restaura a seleção
            if current_row >= 0 and current_row < self.ui.tPinList.rowCount():
                self.ui.tPinList.setCurrentCell(current_row, current_col)
        finally:
            # Desbloqueia sinais após a atualização
            self.ui.tPinList.blockSignals(False)
            
    def getPearsonHash(self, input):
        h=0
        for i in input:
            index=i ^ h
            h=Permutation[index % len(Permutation)]
        return h
    def getNoteString(self, note):
        return noteArray[note%12]+str(int(note/12)-2)+' ('+str(note)+')'
    def selectPin(self):
        """Atualiza os controles da interface com os valores do pin selecionado"""
        # Verifica se há uma linha selecionada
        if self.ui.tPinList.currentRow() < 0:
            return
            
        # Bloqueia sinais para evitar chamadas recursivas durante a atualização
        self.ui.lName.blockSignals(True)
        self.ui.cbType.blockSignals(True)
        self.ui.cbNote.blockSignals(True)
        self.ui.hsThresold.blockSignals(True)
        self.ui.hsScantime.blockSignals(True)
        self.ui.hsMasktime.blockSignals(True)
        self.ui.hsRetrigger.blockSignals(True)
        self.ui.cbCurve.blockSignals(True)
        self.ui.hsCurveform.blockSignals(True)
        self.ui.hsXtalk.blockSignals(True)
        self.ui.hsGain.blockSignals(True)
        self.ui.spXtalkgroup.blockSignals(True)
        self.ui.spChannel.blockSignals(True)
        
        try:
            # Atualiza os controles com os valores do pin selecionado
            self.ui.lName.setText(self.pins[self.ui.tPinList.currentRow()].name.decode())
    
            if self.pins[self.ui.tPinList.currentRow()].type==127:
                self.ui.cbType.setCurrentIndex(3)
            else:
                self.ui.cbType.setCurrentIndex(self.pins[self.ui.tPinList.currentRow()].type)
    
            self.ui.cbNote.setCurrentIndex(self.pins[self.ui.tPinList.currentRow()].note)
    
            self.ui.hsThresold.setValue(self.pins[self.ui.tPinList.currentRow()].thresold)
            self.ui.lThresold.setText(str(self.pins[self.ui.tPinList.currentRow()].thresold))
    
            self.ui.hsScantime.setValue(self.pins[self.ui.tPinList.currentRow()].scantime)
            self.ui.lScantime.setText(str(self.pins[self.ui.tPinList.currentRow()].scantime))
    
            self.ui.hsMasktime.setValue(self.pins[self.ui.tPinList.currentRow()].masktime)
            self.ui.lMasktime.setText(str(self.pins[self.ui.tPinList.currentRow()].masktime))
    
            self.ui.hsRetrigger.setValue(self.pins[self.ui.tPinList.currentRow()].retrigger)
            self.ui.lRetrigger.setText(str(self.pins[self.ui.tPinList.currentRow()].retrigger))
    
            self.ui.cbCurve.setCurrentIndex(self.pins[self.ui.tPinList.currentRow()].curve)
    
            self.ui.hsCurveform.setValue(self.pins[self.ui.tPinList.currentRow()].curveform)
            self.ui.lCurveform.setText(str(self.pins[self.ui.tPinList.currentRow()].curveform))
    
            self.ui.hsXtalk.setValue(self.pins[self.ui.tPinList.currentRow()].xtalk)
            self.ui.lXtalk.setText(str(self.pins[self.ui.tPinList.currentRow()].xtalk))
    
            self.ui.hsGain.setValue(self.pins[self.ui.tPinList.currentRow()].gain)
            self.ui.lGain.setText(str(self.pins[self.ui.tPinList.currentRow()].gain))
    
            self.ui.spXtalkgroup.setValue(self.pins[self.ui.tPinList.currentRow()].xtalkgroup)
            
            self.ui.spChannel.setValue(self.pins[self.ui.tPinList.currentRow()].channel)
        finally:
            # Desbloqueia sinais após a atualização
            self.ui.lName.blockSignals(False)
            self.ui.cbType.blockSignals(False)
            self.ui.cbNote.blockSignals(False)
            self.ui.hsThresold.blockSignals(False)
            self.ui.hsScantime.blockSignals(False)
            self.ui.hsMasktime.blockSignals(False)
            self.ui.hsRetrigger.blockSignals(False)
            self.ui.cbCurve.blockSignals(False)
            self.ui.hsCurveform.blockSignals(False)
            self.ui.hsXtalk.blockSignals(False)
            self.ui.hsGain.blockSignals(False)
            self.ui.spXtalkgroup.blockSignals(False)
            self.ui.spChannel.blockSignals(False)
    def changeMode(self, int):
        mode_name = ""
        if int==0:
            data = 0xF0,0x77,0x01,0x01,0x00,0x00,0xF7
            mode_name = "SETUP"
            self.ui.tabState.setTabText(0, "Configuration ✓")
            self.ui.tabState.setTabText(1, "Tool")
            self.ui.tabState.setTabText(2, "Monitor")
        elif int==1:
            data = 0xF0,0x77,0x01,0x03,0x00,0x00,0xF7
            mode_name = "LOG"
            self.ui.tabState.setTabText(0, "Configuration")
            self.ui.tabState.setTabText(1, "Tool ✓")
            self.ui.tabState.setTabText(2, "Monitor")
        else:
            data = 0xF0,0x77,0x01,0x02,0x00,0x00,0xF7
            mode_name = "MIDI"
            self.ui.tabState.setTabText(0, "Configuration")
            self.ui.tabState.setTabText(1, "Tool")
            self.ui.tabState.setTabText(2, "Monitor ✓")
        
        # Enviar comando sem mostrar mensagens no log
        txData = struct.pack("B"*len(data), *data)
        if hasattr(self, 'ser') and self.ser.isOpen():
            try:
                self.ser.write(txData)
            except Exception as e:
                print(f"Erro ao enviar comando de modo: {e}")
    def selectMIDI(self, port):
        if port>=0:
            try:
                midi_out.close_port()
                midi_out.open_port(port)
                port_name = midi_out.ports[port] if port < len(midi_out.ports) else f"Port {port}"
                self.log(f"Porta MIDI {port_name} selecionada")
            except Exception as e:
                error_msg = f"Erro ao selecionar porta MIDI: {e}"
                print(error_msg)
                self.log(error_msg)
    def reloadMIDI(self):
        self.ui.cbMIDI.clear()
        # Atualiza a lista de portas MIDI
        try:
            # Atualiza a lista de portas
            midi_out.ports = midi_out._get_ports_list()
            self.log("Atualizando lista de portas MIDI...")
            
            # Se não encontrar portas, verifica se o IAC Driver está disponível
            if not midi_out.ports:
                self.log("Nenhuma porta MIDI encontrada. Verificando dispositivos virtuais...")
                midi_out_raw = rtmidi.MidiOut()
                for i in range(midi_out_raw.get_port_count()):
                    port_name = midi_out_raw.get_port_name(i)
                    if "IAC" in port_name:
                        self.log(f"Dispositivo MIDI virtual encontrado: {port_name}")
                        midi_out.ports.append(port_name)
            
            if midi_out.ports:
                self.log(f"Portas MIDI disponíveis: {len(midi_out.ports)}")
                for port_name in midi_out.ports:
                    self.log(f"  - {port_name}")
            else:
                self.log("Nenhuma porta MIDI encontrada")
                
        except Exception as e:
            error_msg = f"Erro ao recarregar portas MIDI: {e}"
            print(error_msg)
            self.log(error_msg)
            midi_out.ports = []
            
        # Adiciona as portas à combobox
        for port_name in midi_out.ports:
            self.ui.cbMIDI.addItem(port_name)
    def editedName(self):
        self.pins[self.ui.tPinList.currentRow()].name=str(self.ui.lName.text()).encode()
        self.updateList()
        
    def editedType(self, int):
        if int==3:
            self.pins[self.ui.tPinList.currentRow()].type=127
        else:
            self.pins[self.ui.tPinList.currentRow()].type=int
        self.updateList()

    def editedThresold(self, int):
        self.pins[self.ui.tPinList.currentRow()].thresold=int
        self.ui.lThresold.setText(str(int))
        self.updateList()

    def editedScantime(self, int):
        self.pins[self.ui.tPinList.currentRow()].scantime=int
        self.ui.lScantime.setText(str(int))
        self.updateList()

    def editedMasktime(self, int):
        self.pins[self.ui.tPinList.currentRow()].masktime=int
        self.ui.lMasktime.setText(str(int))
        self.updateList()

    def editedRetrigger(self, int):
        self.pins[self.ui.tPinList.currentRow()].retrigger=int
        self.ui.lRetrigger.setText(str(int))
        
    def editedNote(self, int):
        self.pins[self.ui.tPinList.currentRow()].note=int
        self.updateList()

    def editedCurve(self, int):
        self.pins[self.ui.tPinList.currentRow()].curve=int

    def editedCurveform(self, int):
        self.pins[self.ui.tPinList.currentRow()].curveform=int
        self.ui.lCurveform.setText(str(int))

    def editedXtalk(self, int):
        self.pins[self.ui.tPinList.currentRow()].xtalk=int
        self.ui.lXtalk.setText(str(int))

    def editedXtalkgroup(self, int):
        self.pins[self.ui.tPinList.currentRow()].xtalkgroup=int

    def editedChannel(self, int):
        self.pins[self.ui.tPinList.currentRow()].channel=int

    def editedGain(self, int):
        self.pins[self.ui.tPinList.currentRow()].gain=int
        self.ui.lGain.setText(str(int))
    def uploadAll(self):
        """Solicita todos os parâmetros do pin atual do Arduino (Get All)"""
        pin_num = self.ui.tPinList.currentRow()
        self.log(f"Solicitando todos os parâmetros do pin {pin_num} do Arduino...")
        data = 0xF0,0x77,0x02,pin_num,0x7F,0x00,0xF7
        print(data)
        txData = struct.pack("B"*len(data), *data)
        if hasattr(self, 'ser') and self.ser.isOpen():
            self.ser.write(txData)
            self.log(f"Comando Get All enviado para o pin {pin_num}")
        else:
            self.log("Erro: Porta serial não está aberta")
            
    def downloadAll(self):
        """Envia todos os parâmetros do pin atual para o Arduino (Set All)"""
        pin_num = self.ui.tPinList.currentRow()
        self.log(f"Enviando todos os parâmetros do pin {pin_num} para o Arduino...")
        
        # Envia os parâmetros um por um
        self.downloadType()
        time.sleep(0.2)
        self.downloadNote()
        time.sleep(0.2)
        self.downloadThresold()
        time.sleep(0.2)
        self.downloadScantime()
        time.sleep(0.2)
        self.downloadMasktime()
        time.sleep(0.2)
        self.downloadRetrigger()
        time.sleep(0.2)
        self.downloadCurve()
        time.sleep(0.2)
        self.downloadCurveform()
        time.sleep(0.2)
        self.downloadXtalk()
        time.sleep(0.2)
        self.downloadXtalkgroup()
        time.sleep(0.2)
        self.downloadGain()
        
        # Salva as configurações no arquivo pins.ini após enviar todos os parâmetros
        self.save_pins_to_file()
        
        self.log(f"Todos os parâmetros do pin {pin_num} foram enviados com sucesso")
    def uploadType(self):
        """Solicita o tipo do pin atual do Arduino"""
        pin_num = self.ui.tPinList.currentRow()
        self.log(f"Solicitando tipo do pin {pin_num} do Arduino...")
        data = 0xF0,0x77,0x02,pin_num,0x0D,0x00,0xF7
        txData = struct.pack("B"*len(data), *data)
        if hasattr(self, 'ser') and self.ser.isOpen():
            self.ser.write(txData)
        else:
            self.log("Erro: Porta serial não está aberta")
            
    def downloadType(self):
        code=0x03
        if self.ui.ckSave.isChecked()==True:
            code=0x04
        pin_num = self.ui.tPinList.currentRow()
        pin_type = self.pins[pin_num].type
        data = 0xF0,0x77,code,pin_num,0x0D,pin_type,0xF7
        
        # Log da operação
        type_name = self.pinType.get(pin_type, f"Tipo {pin_type}")
        self.log(f"Enviando parâmetro: Pin {pin_num}, Type = {type_name}")
        
        txData = struct.pack("B"*len(data), *data)
        if hasattr(self, 'ser') and self.ser.isOpen():
            self.ser.write(txData)
            # Salva as configurações no arquivo pins.ini após enviar para o Arduino
            self.save_pins_to_file()
        else:
            self.log("Erro: Porta serial não está aberta")

    def uploadNote(self):
        """Solicita a nota MIDI do pin atual do Arduino"""
        pin_num = self.ui.tPinList.currentRow()
        self.log(f"Solicitando nota MIDI do pin {pin_num} do Arduino...")
        data = 0xF0,0x77,0x02,pin_num,0x00,0x00,0xF7
        txData = struct.pack("B"*len(data), *data)
        if hasattr(self, 'ser') and self.ser.isOpen():
            self.ser.write(txData)
        else:
            self.log("Erro: Porta serial não está aberta")
            
    def uploadCurve(self):
        data = 0xF0,0x77,0x02,self.ui.tPinList.currentRow(),0x05,0x00,0xF7
        print(data)
        txData = struct.pack("B"*len(data), *data)
        if self.ser.isOpen():
            self.ser.write(txData)

    def uploadCurveform(self):
        data = 0xF0,0x77,0x02,self.ui.tPinList.currentRow(),0x08,0x00,0xF7
        print(data)
        txData = struct.pack("B"*len(data), *data)
        if self.ser.isOpen():
            self.ser.write(txData)

    def uploadXtalk(self):
        data = 0xF0,0x77,0x02,self.ui.tPinList.currentRow(),0x06,0x00,0xF7
        print(data)
        txData = struct.pack("B"*len(data), *data)
        if self.ser.isOpen():
            self.ser.write(txData)

    def uploadXtalkgroup(self):
        data = 0xF0,0x77,0x02,self.ui.tPinList.currentRow(),0x07,0x00,0xF7
        print(data)
        txData = struct.pack("B"*len(data), *data)
        if self.ser.isOpen():
            self.ser.write(txData)

    def uploadChannel(self):
        data = 0xF0,0x77,0x02,self.ui.tPinList.currentRow(),0x0E,0x00,0xF7
        print(data)
        txData = struct.pack("B"*len(data), *data)
        if self.ser.isOpen():
            self.ser.write(txData)

    def uploadGain(self):
        data = 0xF0,0x77,0x02,self.ui.tPinList.currentRow(),0x09,0x00,0xF7
        print(data)
        txData = struct.pack("B"*len(data), *data)
        if self.ser.isOpen():
            self.ser.write(txData)
             
    def downloadCurve(self):
        code=0x03
        if self.ui.ckSave.isChecked()==True:
            code=0x04
        data = 0xF0,0x77,code,self.ui.tPinList.currentRow(),0x05,self.pins[self.ui.tPinList.currentRow()].curve,0xF7
        print(data)
        txData = struct.pack("B"*len(data), *data)
        if self.ser.isOpen():
            self.ser.write(txData)

    def downloadCurveform(self):
        code=0x03
        if self.ui.ckSave.isChecked()==True:
            code=0x04
        data = 0xF0,0x77,code,self.ui.tPinList.currentRow(),0x08,self.pins[self.ui.tPinList.currentRow()].curveform,0xF7
        print(data)
        txData = struct.pack("B"*len(data), *data)
        if self.ser.isOpen():
            self.ser.write(txData)

    def downloadXtalk(self):
        code=0x03
        if self.ui.ckSave.isChecked()==True:
            code=0x04
        data = 0xF0,0x77,code,self.ui.tPinList.currentRow(),0x06,self.pins[self.ui.tPinList.currentRow()].xtalk,0xF7
        print(data)
        txData = struct.pack("B"*len(data), *data)
        if self.ser.isOpen():
            self.ser.write(txData)

    def downloadXtalkgroup(self):
        code=0x03
        if self.ui.ckSave.isChecked()==True:
            code=0x04
        data = 0xF0,0x77,code,self.ui.tPinList.currentRow(),0x07,self.pins[self.ui.tPinList.currentRow()].xtalkgroup,0xF7
        print(data)
        txData = struct.pack("B"*len(data), *data)
        if self.ser.isOpen():
            self.ser.write(txData)

    def downloadChannel(self):
        code=0x03
        if self.ui.ckSave.isChecked()==True:
            code=0x04
        data = 0xF0,0x77,code,self.ui.tPinList.currentRow(),0x0E,self.pins[self.ui.tPinList.currentRow()].channel,0xF7
        print(data)
        txData = struct.pack("B"*len(data), *data)
        if self.ser.isOpen():
            self.ser.write(txData)

    def downloadGain(self):
        code=0x03
        if self.ui.ckSave.isChecked()==True:
            code=0x04
        data = 0xF0,0x77,code,self.ui.tPinList.currentRow(),0x09,self.pins[self.ui.tPinList.currentRow()].gain,0xF7
        print(data)
        txData = struct.pack("B"*len(data), *data)
        if self.ser.isOpen():
            self.ser.write(txData)
    
    def downloadNote(self):
        code=0x03
        if self.ui.ckSave.isChecked()==True:
            code=0x04
        pin_num = self.ui.tPinList.currentRow()
        note_val = self.pins[pin_num].note
        data = 0xF0,0x77,code,pin_num,0x00,note_val,0xF7
        
        # Log da operação
        note_name = self.getNoteString(note_val)
        self.log(f"Enviando parâmetro: Pin {pin_num}, Note = {note_name}")
        
        txData = struct.pack("B"*len(data), *data)
        if hasattr(self, 'ser') and self.ser.isOpen():
            self.ser.write(txData)
        else:
            self.log("Erro: Porta serial não está aberta")

    def uploadThresold(self):
        data = 0xF0,0x77,0x02,self.ui.tPinList.currentRow(),0x01,0x00,0xF7
        print(data)
        txData = struct.pack("B"*len(data), *data)
        if self.ser.isOpen():
            self.ser.write(txData)

    def downloadThresold(self):
        code=0x03
        if self.ui.ckSave.isChecked()==True:
            code=0x04
        pin_num = self.ui.tPinList.currentRow()
        thresold_val = self.pins[pin_num].thresold
        data = 0xF0,0x77,code,pin_num,0x01,thresold_val,0xF7
        
        # Log da operação
        self.log(f"Enviando parâmetro: Pin {pin_num}, Threshold = {thresold_val}")
        
        txData = struct.pack("B"*len(data), *data)
        if hasattr(self, 'ser') and self.ser.isOpen():
            self.ser.write(txData)
        else:
            self.log("Erro: Porta serial não está aberta")

    def uploadScantime(self):
        data = 0xF0,0x77,0x02,self.ui.tPinList.currentRow(),0x02,0x00,0xF7
        print(data)
        txData = struct.pack("B"*len(data), *data)
        if self.ser.isOpen():
            self.ser.write(txData)
            
    def downloadScantime(self):
        code=0x03
        if self.ui.ckSave.isChecked()==True:
            code=0x04
        data = 0xF0,0x77,code,self.ui.tPinList.currentRow(),0x02,self.pins[self.ui.tPinList.currentRow()].scantime,0xF7
        print(data)
        txData = struct.pack("B"*len(data), *data)
        if self.ser.isOpen():
            self.ser.write(txData)

    def uploadMasktime(self):
        data = 0xF0,0x77,0x02,self.ui.tPinList.currentRow(),0x03,0x00,0xF7
        print(data)
        txData = struct.pack("B"*len(data), *data)
        if self.ser.isOpen():
            self.ser.write(txData)
            
    def downloadMasktime(self):
        code=0x03
        if self.ui.ckSave.isChecked()==True:
            code=0x04
        data = 0xF0,0x77,code,self.ui.tPinList.currentRow(),0x03,self.pins[self.ui.tPinList.currentRow()].masktime,0xF7
        print(data)
        txData = struct.pack("B"*len(data), *data)
        if self.ser.isOpen():
            self.ser.write(txData)

    def uploadRetrigger(self):
        data = 0xF0,0x77,0x02,self.ui.tPinList.currentRow(),0x04,0x00,0xF7
        print(data)
        txData = struct.pack("B"*len(data), *data)
        if self.ser.isOpen():
            self.ser.write(txData)
            
    def downloadRetrigger(self):
        code=0x03
        if self.ui.ckSave.isChecked()==True:
            code=0x04
        data = 0xF0,0x77,code,self.ui.tPinList.currentRow(),0x04,self.pins[self.ui.tPinList.currentRow()].retrigger,0xF7
        print(data)
        txData = struct.pack("B"*len(data), *data)
        if self.ser.isOpen():
            self.ser.write(txData)
    def handle_updateMonitor(self, data1, data2, data3):
        for i in range(0, len(self.pbPinArray)):
            if self.pins[i].note==data2:
                self.pbPinArray[i].setFormat("    "+self.pins[i].name.decode()+" %v    ")
                self.pbPinArray[i].setValue(data3)
            
        if (data1&0xF0)==0x90:
            message = "NOTE ON ("+str(data2)+","+str(data3)+")"
            self.ui.lMIDIHistory.addItem(message)
            self.log(f"MIDI: {message}")
        elif (data1&0xF0)==0xB0:
            message = "CC ("+str(data2)+","+str(data3)+")"
            self.ui.lMIDIHistory.addItem(message)
            self.log(f"MIDI: {message}")
        if self.ui.lMIDIHistory.count() > 20:
            self.ui.lMIDIHistory.takeItem(0)
        self.ui.lMIDIHistory.setCurrentRow(self.ui.lMIDIHistory.count()-1)
    def disableAllPins(self):
        """Desabilita todos os pinos configurando-os como 'Disabled'"""
        # Exibe mensagem de confirmação
        reply = QtWidgets.QMessageBox.question(
            self, 
            'Desabilitar todos os pinos',
            'Esta ação irá definir todos os pinos como "Disabled".\n\nDeseja continuar?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.log("Desabilitando todos os pinos...")
            
            # Define todos os pinos como 'Disabled' (tipo 127)
            for i in range(len(self.pins)):
                self.pins[i].type = 127
                
                # Envia o comando para o Arduino se estiver conectado
                if hasattr(self, 'ser') and self.ser.isOpen():
                    code = 0x03
                    if self.ui.ckSave.isChecked():
                        code = 0x04
                    data = 0xF0, 0x77, code, i, 0x0D, 127, 0xF7
                    txData = struct.pack("B"*len(data), *data)
                    self.ser.write(txData)
                    time.sleep(0.05)  # Pequeno delay entre comandos
                    
                    # Processa eventos para manter a interface responsiva
                    QtWidgets.QApplication.processEvents()
            
            # Salva as configurações no arquivo pins.ini
            self.save_pins_to_file()
            
            # Atualiza a interface
            self.updateList()
            
            # Seleciona o primeiro item da lista para mostrar os detalhes
            self.ui.tPinList.setCurrentCell(0, 0)
            self.selectPin()
            
            self.log("Todos os pinos foram desabilitados com sucesso")
            QtWidgets.QMessageBox.information(
                self, 
                'Operação concluída',
                'Todos os pinos foram desabilitados com sucesso.',
                QtWidgets.QMessageBox.Ok
            )
    def addDisableAllButton(self):
        """Adiciona o botão para desabilitar todos os pinos na aba de configuração"""
        # Cria o botão no widget central
        self.ui.btnDisableAll = QtWidgets.QPushButton(self.ui.centralwidget)
        self.ui.btnDisableAll.setGeometry(310, 10, 130, 22)
        self.ui.btnDisableAll.setText("Desabilitar Todos")
        self.ui.btnDisableAll.setToolTip("Define todos os pinos como 'Disabled'")
        
        # Conecta o botão à função disableAllPins
        self.ui.btnDisableAll.clicked.connect(self.disableAllPins)