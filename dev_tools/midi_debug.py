#!/usr/bin/env python3
"""
Ferramenta de diagnóstico para conexões MIDI no macOS
"""

import sys
import time
import rtmidi

def list_midi_ports():
    """Lista todas as portas MIDI disponíveis"""
    print("=== Portas MIDI Disponíveis ===")
    
    # Verificar portas de entrada
    midi_in = rtmidi.MidiIn()
    in_ports = midi_in.get_ports()
    print("\nPortas de Entrada MIDI:")
    if in_ports:
        for i, port in enumerate(in_ports):
            print(f"  {i}: {port}")
    else:
        print("  Nenhuma porta de entrada MIDI encontrada")
    
    # Verificar portas de saída
    midi_out = rtmidi.MidiOut()
    out_ports = midi_out.get_ports()
    print("\nPortas de Saída MIDI:")
    if out_ports:
        for i, port in enumerate(out_ports):
            print(f"  {i}: {port}")
    else:
        print("  Nenhuma porta de saída MIDI encontrada")
    
    # Verificar especificamente o IAC Driver
    iac_ports = [p for p in out_ports if "IAC" in p]
    print("\nPortas IAC Driver:")
    if iac_ports:
        for port in iac_ports:
            print(f"  {port}")
    else:
        print("  Nenhuma porta IAC Driver encontrada")
        print("  Verifique se o IAC Driver está ativado na Configuração Áudio e MIDI")

def test_midi_output(port_name=None, port_index=None):
    """Testa o envio de mensagens MIDI para uma porta específica"""
    midi_out = rtmidi.MidiOut()
    ports = midi_out.get_ports()
    
    if not ports:
        print("Nenhuma porta MIDI de saída disponível")
        return False
    
    # Selecionar porta por nome ou índice
    selected_port = None
    if port_name:
        for i, port in enumerate(ports):
            if port_name.lower() in port.lower():
                selected_port = i
                break
        if selected_port is None:
            print(f"Porta '{port_name}' não encontrada")
            return False
    elif port_index is not None:
        if 0 <= port_index < len(ports):
            selected_port = port_index
        else:
            print(f"Índice de porta inválido: {port_index}")
            return False
    else:
        # Se nenhuma porta for especificada, procura por IAC
        for i, port in enumerate(ports):
            if "IAC" in port:
                selected_port = i
                break
        if selected_port is None:
            print("Nenhuma porta IAC encontrada e nenhuma porta especificada")
            return False
    
    # Abrir a porta selecionada
    try:
        midi_out.open_port(selected_port)
        port_name = ports[selected_port]
        print(f"Porta aberta: {port_name}")
        
        # Enviar algumas notas MIDI
        print(f"Enviando notas MIDI para {port_name}...")
        for note in [60, 64, 67, 72]:  # C E G C (acorde de C maior)
            print(f"Enviando nota {note}")
            midi_out.send_message([0x90, note, 100])  # Note On, nota, velocidade
            time.sleep(0.5)
            midi_out.send_message([0x80, note, 0])    # Note Off
            time.sleep(0.1)
        
        print("Teste concluído com sucesso!")
        midi_out.close_port()
        return True
    except Exception as e:
        print(f"Erro ao testar porta MIDI: {e}")
        return False

def monitor_midi_input(port_name=None, port_index=None, duration=10):
    """Monitora mensagens MIDI recebidas em uma porta específica"""
    midi_in = rtmidi.MidiIn()
    ports = midi_in.get_ports()
    
    if not ports:
        print("Nenhuma porta MIDI de entrada disponível")
        return False
    
    # Selecionar porta por nome ou índice
    selected_port = None
    if port_name:
        for i, port in enumerate(ports):
            if port_name.lower() in port.lower():
                selected_port = i
                break
        if selected_port is None:
            print(f"Porta '{port_name}' não encontrada")
            return False
    elif port_index is not None:
        if 0 <= port_index < len(ports):
            selected_port = port_index
        else:
            print(f"Índice de porta inválido: {port_index}")
            return False
    else:
        # Se nenhuma porta for especificada, procura por IAC
        for i, port in enumerate(ports):
            if "IAC" in port:
                selected_port = i
                break
        if selected_port is None:
            print("Nenhuma porta IAC encontrada e nenhuma porta especificada")
            return False
    
    # Abrir a porta selecionada
    try:
        midi_in.open_port(selected_port)
        port_name = ports[selected_port]
        print(f"Monitorando porta: {port_name} por {duration} segundos...")
        print("Toque algum instrumento MIDI ou envie mensagens MIDI para esta porta")
        
        # Configurar callback para mensagens MIDI
        class MidiInputHandler:
            def __init__(self):
                self.received = False
                
            def __call__(self, event, data=None):
                message, deltatime = event
                self.received = True
                print(f"Mensagem MIDI recebida: {message}, tempo: {deltatime}")
        
        handler = MidiInputHandler()
        midi_in.set_callback(handler)
        
        # Monitorar por um período
        start_time = time.time()
        while time.time() - start_time < duration:
            time.sleep(0.1)
            if handler.received:
                print("Mensagens MIDI detectadas com sucesso!")
                break
        
        if not handler.received:
            print("Nenhuma mensagem MIDI recebida durante o período de monitoramento")
        
        midi_in.close_port()
        return handler.received
    except Exception as e:
        print(f"Erro ao monitorar porta MIDI: {e}")
        return False

def test_midi_loopback():
    """Testa o loopback MIDI usando o IAC Driver"""
    print("=== Teste de Loopback MIDI ===")
    print("Este teste verifica se o IAC Driver está funcionando corretamente")
    print("Enviando mensagens MIDI para o IAC Driver e verificando se elas são recebidas")
    
    # Encontrar portas IAC
    midi_out = rtmidi.MidiOut()
    out_ports = midi_out.get_ports()
    iac_out_ports = [i for i, p in enumerate(out_ports) if "IAC" in p]
    
    midi_in = rtmidi.MidiIn()
    in_ports = midi_in.get_ports()
    iac_in_ports = [i for i, p in enumerate(in_ports) if "IAC" in p]
    
    if not iac_out_ports or not iac_in_ports:
        print("Portas IAC Driver não encontradas. Verifique se o IAC Driver está ativado.")
        return False
    
    # Abrir portas
    try:
        midi_out.open_port(iac_out_ports[0])
        midi_in.open_port(iac_in_ports[0])
        
        print(f"Porta de saída: {out_ports[iac_out_ports[0]]}")
        print(f"Porta de entrada: {in_ports[iac_in_ports[0]]}")
        
        # Configurar callback para mensagens MIDI
        received_notes = []
        class MidiInputHandler:
            def __call__(self, event, data=None):
                message, deltatime = event
                if len(message) >= 3 and message[0] == 0x90:  # Note On
                    received_notes.append(message[1])
                    print(f"Nota recebida: {message[1]}")
        
        handler = MidiInputHandler()
        midi_in.set_callback(handler)
        
        # Enviar algumas notas MIDI
        test_notes = [60, 64, 67, 72]
        print("Enviando notas de teste...")
        for note in test_notes:
            print(f"Enviando nota {note}")
            midi_out.send_message([0x90, note, 100])  # Note On
            time.sleep(0.5)
            midi_out.send_message([0x80, note, 0])    # Note Off
            time.sleep(0.1)
        
        # Verificar se todas as notas foram recebidas
        time.sleep(1)  # Esperar um pouco para garantir que todas as mensagens foram processadas
        success = all(note in received_notes for note in test_notes)
        
        if success:
            print("Teste de loopback bem-sucedido! Todas as notas foram recebidas.")
        else:
            print("Teste de loopback falhou. Algumas notas não foram recebidas.")
            print(f"Notas enviadas: {test_notes}")
            print(f"Notas recebidas: {received_notes}")
        
        midi_in.close_port()
        midi_out.close_port()
        return success
    except Exception as e:
        print(f"Erro durante o teste de loopback: {e}")
        return False

def main():
    """Função principal"""
    print("=== Ferramenta de Diagnóstico MIDI ===")
    print("Esta ferramenta ajuda a diagnosticar problemas com conexões MIDI no macOS")
    
    # Listar portas MIDI disponíveis
    list_midi_ports()
    
    # Menu de opções
    while True:
        print("\n=== Menu de Diagnóstico ===")
        print("1. Listar portas MIDI")
        print("2. Testar envio de MIDI para IAC Driver")
        print("3. Monitorar entrada MIDI")
        print("4. Testar loopback MIDI (IAC Driver)")
        print("5. Sair")
        
        choice = input("Escolha uma opção (1-5): ")
        
        if choice == "1":
            list_midi_ports()
        elif choice == "2":
            port_name = input("Nome da porta (deixe em branco para IAC Driver): ")
            if port_name:
                test_midi_output(port_name=port_name)
            else:
                test_midi_output()
        elif choice == "3":
            port_name = input("Nome da porta (deixe em branco para IAC Driver): ")
            duration = input("Duração do monitoramento em segundos (padrão: 10): ")
            try:
                duration = int(duration) if duration else 10
            except ValueError:
                duration = 10
            if port_name:
                monitor_midi_input(port_name=port_name, duration=duration)
            else:
                monitor_midi_input(duration=duration)
        elif choice == "4":
            test_midi_loopback()
        elif choice == "5":
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()