#!/usr/bin/env python3
import rtmidi
import time
import sys
import select

def init_midi():
    try:
        # Inicializar MIDI output
        midi_out = rtmidi.MidiOut()
        ports = midi_out.get_ports()
        
        if not ports:
            print("Nenhum dispositivo MIDI de saída encontrado.")
            print("Verifique se o IAC Driver está ativado em Configuração Áudio e MIDI.")
            return None
        
        # Conectar ao primeiro dispositivo disponível (IAC Driver)
        midi_out.open_port(0)
        print(f"Conectado ao dispositivo MIDI: {ports[0]}")
        return midi_out
    
    except Exception as e:
        print(f"Erro ao inicializar MIDI: {e}")
        return None

def connect_to_microdrum():
    try:
        import serial
        import serial.tools.list_ports
        
        # Listar portas seriais disponíveis
        ports = list(serial.tools.list_ports.comports())
        if not ports:
            print("Nenhuma porta serial encontrada.")
            return False
        
        print("Portas seriais disponíveis:")
        for i, port in enumerate(ports):
            print(f"  {i}: {port.device} - {port.description}")
        
        # Tentar encontrar a porta do Arduino/MicroDrum
        arduino_port = None
        for port in ports:
            if "Arduino" in port.description or "CH340" in port.description or "USB Serial" in port.description:
                arduino_port = port.device
                break
        
        if not arduino_port and ports:
            # Se não encontrou automaticamente, use a primeira porta disponível
            arduino_port = ports[0].device
            
        if arduino_port:
            print(f"Conectando ao MicroDrum na porta {arduino_port}...")
            # Conectar na velocidade padrão do MicroDrum (115200 ou 31250 para MIDI)
            ser = serial.Serial(arduino_port, 115200, timeout=1)
            print("Conexão estabelecida com o hardware MicroDrum!")
            return ser
        else:
            print("Não foi possível encontrar o hardware MicroDrum.")
            return False
            
    except ImportError:
        print("Biblioteca pyserial não encontrada. Instale com: pip install pyserial")
        return False
    except Exception as e:
        print(f"Erro ao conectar ao MicroDrum: {e}")
        return False

def process_midi_message(midi_out, note, velocity):
    """Processa uma mensagem MIDI recebida do MicroDrum e encaminha para o dispositivo virtual"""
    try:
        # Canal 9 (10 em base 1) é o canal padrão de percussão
        channel = 9
        # Note On (0x90 | channel)
        status_byte = 0x90 | channel
        midi_out.send_message([status_byte, note, velocity])
        print(f"MIDI enviado: Nota {note}, Velocidade {velocity}")
        
        # Enviar Note Off após um curto período para evitar notas presas
        if velocity > 0:
            time.sleep(0.05)  # 50ms de duração da nota
            midi_out.send_message([0x80 | channel, note, 0])
    except Exception as e:
        print(f"Erro ao enviar MIDI: {e}")

def send_config_to_microdrum(serial_conn):
    """Envia configuração inicial para o MicroDrum"""
    try:
        # Enviar comando para ativar modo MIDI
        serial_conn.write(b'M')  # 'M' para modo MIDI
        time.sleep(0.1)
        return True
    except Exception as e:
        print(f"Erro ao configurar MicroDrum: {e}")
        return False

def main():
    print("Iniciando MicroDrum Config Tool")
    
    # Inicializar MIDI
    midi_out = init_midi()
    if not midi_out:
        print("Falha ao inicializar MIDI. Saindo.")
        sys.exit(1)
    
    # Conectar ao hardware MicroDrum
    serial_conn = connect_to_microdrum()
    if not serial_conn:
        print("Continuando sem conexão com hardware. Apenas modo virtual disponível.")
    else:
        # Configurar o MicroDrum
        if send_config_to_microdrum(serial_conn):
            print("MicroDrum configurado com sucesso!")
    
    print("MicroDrum Config Tool inicializado com sucesso!")
    print("Pressione Ctrl+C para sair")
    print("Comandos disponíveis:")
    print("  T - Testar pads (envia notas de teste)")
    print("  R - Reiniciar conexão com MicroDrum")
    print("  Q - Sair")
    
    try:
        # Buffer para armazenar dados parciais
        buffer = bytearray()
        
        # Loop principal
        while True:
            # Verificar entrada do usuário
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                cmd = sys.stdin.read(1)
                if cmd.upper() == 'Q':
                    print("Saindo...")
                    break
                elif cmd.upper() == 'T':
                    print("Enviando notas de teste...")
                    # Enviar algumas notas de teste
                    for note in [36, 38, 42, 46]:
                        process_midi_message(midi_out, note, 100)
                        time.sleep(0.2)
                elif cmd.upper() == 'R':
                    print("Reiniciando conexão com MicroDrum...")
                    if serial_conn and hasattr(serial_conn, 'close'):
                        serial_conn.close()
                    serial_conn = connect_to_microdrum()
                    if serial_conn:
                        send_config_to_microdrum(serial_conn)
            
            if serial_conn:
                # Ler dados do MicroDrum se estiver conectado
                if serial_conn.in_waiting > 0:
                    # Ler um byte de cada vez para processar mensagens MIDI corretamente
                    byte = serial_conn.read(1)
                    buffer.extend(byte)
                    
                    # Processar mensagens MIDI completas (3 bytes)
                    while len(buffer) >= 3:
                        # Verificar se o primeiro byte é um status byte MIDI
                        if 0x80 <= buffer[0] <= 0xEF:
                            # Extrair a mensagem MIDI
                            status = buffer[0]
                            data1 = buffer[1]
                            data2 = buffer[2]
                            
                            # Processar Note On
                            if 0x90 <= status <= 0x9F:
                                process_midi_message(midi_out, data1, data2)
                            
                            # Remover os 3 bytes processados
                            buffer = buffer[3:]
                        else:
                            # Se não for um status byte válido, descartar e continuar
                            buffer.pop(0)
            
            # Pequena pausa para não sobrecarregar a CPU
            time.sleep(0.001)
    except KeyboardInterrupt:
        print("\nEncerrando MicroDrum Config Tool")
    except Exception as e:
        print(f"Erro inesperado: {e}")
    finally:
        # Limpar recursos
        if midi_out:
            midi_out.close_port()
        if serial_conn and hasattr(serial_conn, 'close'):
            serial_conn.close()

if __name__ == "__main__":
    main()