#!/usr/bin/env python3
"""
Wrapper para rtmidi.MidiOut que adiciona o atributo ports
"""

import rtmidi

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