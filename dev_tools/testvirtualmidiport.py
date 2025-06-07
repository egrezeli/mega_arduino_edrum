#!/usr/bin/env python3
import rtmidi
import time

# Listar dispositivos MIDI disponíveis
midi_out = rtmidi.MidiOut()
ports = midi_out.get_ports()

print("Dispositivos MIDI de saída disponíveis:")
for i, port in enumerate(ports):
    print(f"  {i}: {port}")

midi_in = rtmidi.MidiIn()
ports = midi_in.get_ports()

print("\nDispositivos MIDI de entrada disponíveis:")
for i, port in enumerate(ports):
    print(f"  {i}: {port}")

# Testar envio de mensagens MIDI para o IAC Driver
try:
    # Abrir a porta de saída (IAC Driver)
    if ports:
        midi_out.open_port(0)
        print("\nEnviando notas MIDI para o IAC Driver...")
        
        # Enviar algumas notas de bateria (canal 9 = canal de percussão)
        # Nota 36 = Kick drum, 38 = Snare, 42 = Hi-hat closed
        for note in [36, 38, 42]:
            print(f"Enviando nota {note}")
            # Note On (0x90 | canal 9)
            midi_out.send_message([0x99, note, 100])  # Velocidade 100
            time.sleep(0.3)
            # Note Off
            midi_out.send_message([0x89, note, 0])
            time.sleep(0.2)
        
        print("Teste de envio MIDI concluído com sucesso!")
        midi_out.close_port()
    else:
        print("Nenhuma porta MIDI disponível para teste.")
except Exception as e:
    print(f"Erro ao testar MIDI: {e}")
