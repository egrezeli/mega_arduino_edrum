#!/usr/bin/env python3
"""
Monkey patch para rtmidi para adicionar o atributo 'ports' que é usado pelo MicroDrum Config Tool
"""

import rtmidi

# Salva a classe original
original_midiout = rtmidi.MidiOut

# Cria uma classe wrapper que adiciona o atributo 'ports'
class MidiOutWithPorts(rtmidi.MidiOut):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ports = self.get_ports()
    
    def get_ports(self):
        """Retorna a lista de portas disponíveis"""
        ports = []
        count = self.get_port_count()
        for i in range(count):
            ports.append(self.get_port_name(i))
        return ports

# Substitui a classe original pela classe wrapper
rtmidi.MidiOut = MidiOutWithPorts

print("rtmidi.MidiOut foi modificado para incluir o atributo 'ports'")