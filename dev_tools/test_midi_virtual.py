#!/usr/bin/env python3
"""
Script para testar o dispositivo MIDI virtual com o MicroDrum
"""
import rtmidi
import time
import sys

def list_midi_ports():
    """Lista todas as portas MIDI disponíveis"""
    midi_out = rtmidi.MidiOut()
    ports = []
    count = midi_out.get_port_count()
    
    print("Portas MIDI de saída disponíveis:")
    for i in range(count):
        port_name = midi_out.get_port_name(i)
        ports.append(port_name)
        print(f"  {i}: {port_name}")
    
    midi_in = rtmidi.MidiIn()
    in_ports = []
    count = midi_in.get_port_count()
    
    print("\nPortas MIDI de entrada disponíveis:")
    for i in range(count):
        port_name = midi_in.get_port_name(i)
        in_ports.append(port_name)
        print(f"  {i}: {port_name}")
    
    return ports, in_ports

def send_test_notes(port_name=None):
    """Envia notas de teste para uma porta MIDI específica ou a primeira disponível"""
    midi_out = rtmidi.MidiOut()
    ports = []
    count = midi_out.get_port_count()
    
    for i in range(count):
        ports.append(midi_out.get_port_name(i))
    
    port_index = -1
    if port_name:
        for i, name in enumerate(ports):
            if port_name in name:
                port_index = i
                break
    else:
        if ports:
            port_index = 0
    
    if port_index >= 0:
        print(f"Conectando à porta MIDI: {ports[port_index]}")
        midi_out.open_port(port_index)
        
        # Notas de bateria comuns
        drum_notes = {
            "Kick": 36,
            "Snare": 38,
            "Hi-hat Closed": 42,
            "Hi-hat Open": 46,
            "Crash": 49,
            "Ride": 51,
            "Tom 1": 48,
            "Tom 2": 45,
            "Tom 3": 43
        }
        
        # Canal 9 (10 em base 1) é o canal padrão de percussão
        channel = 9
        
        print("Enviando notas de bateria...")
        for name, note in drum_notes.items():
            print(f"Tocando {name} (nota {note})")
            # Note On (0x90 | channel)
            midi_out.send_message([0x90 | channel, note, 100])
            time.sleep(0.3)
            # Note Off
            midi_out.send_message([0x80 | channel, note, 0])
            time.sleep(0.1)
        
        print("Teste concluído!")
        midi_out.close_port()
    else:
        print("Nenhuma porta MIDI disponível para teste.")

if __name__ == "__main__":
    print("Testando dispositivo MIDI virtual...")
    ports, in_ports = list_midi_ports()
    
    # Procura pelo IAC Driver
    iac_port = None
    for port in ports:
        if "IAC" in port:
            iac_port = port
            break
    
    if iac_port:
        print(f"\nEncontramos o IAC Driver: {iac_port}")
        choice = input("Deseja enviar notas de teste para este dispositivo? (s/n): ")
        if choice.lower() == 's':
            send_test_notes(iac_port)
    else:
        print("\nNenhum dispositivo IAC Driver encontrado.")
        print("Configure o IAC Driver em Configuração Áudio e MIDI primeiro.")
        
    print("\nPara usar o IAC Driver com o MicroDrum Config Tool:")
    print("1. Execute o script run.sh")
    print("2. Selecione o IAC Driver na lista de dispositivos MIDI")
    print("3. Configure seu software de bateria para receber MIDI do IAC Driver")