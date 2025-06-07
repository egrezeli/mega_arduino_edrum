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
    from PyQt5.QtCore import qRegisterMetaType
    qRegisterMetaType('QVector<int>')
except (ImportError, TypeError) as e:
    print(f"Erro ao registrar QVector<int>: {e}")

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
serialSpeed=115200

if fluidsynth_available:
    fs = fluidsynth.Synth()
    fs.start()
    sfid = fs.sfload("example.sf2")
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
    updateMonitor = pyqtSignal(int,int,int)
    logMessage = pyqtSignal(str)
    
    @staticmethod
    def register_meta_types():
        # Registrar tipos personalizados para uso em sinais/slots entre threads
        from PyQt5.QtCore import QVector
        try:
            from PyQt5.QtCore import qRegisterMetaType
            qRegisterMetaType('QVector<int>')
        except Exception:
            pass
