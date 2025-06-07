# Correção para Snare Drum no MicroDrum

## Problema Identificado

O problema com a snare drum não sendo reconhecida pelo Addictive Drums 2 tem duas causas:

1. **Nota incorreta**: O MicroDrum está enviando a nota 0, mas o padrão General MIDI para snare é a nota 38.
2. **Velocidade zero**: A velocidade 0 em MIDI significa "note off" (desligar nota), não um toque leve.

## Solução: Tradutor MIDI Aprimorado

Foi criado um tradutor MIDI aprimorado (`midi_translator_enhanced.py`) que:

1. **Mapeia as notas**: Converte a nota 0 do MicroDrum para a nota 38 (snare padrão)
2. **Corrige velocidades**: Garante que a velocidade nunca seja zero para notas ativas
3. **Interface de configuração**: Permite ajustar o mapeamento de notas em tempo real

## Como usar o Tradutor MIDI Aprimorado

1. Execute o tradutor MIDI aprimorado:
   ```bash
   ./midi_translator_enhanced.py
   ```

2. Configure:
   - Selecione a porta serial do Arduino
   - Mantenha o baud rate em 115200
   - Selecione a porta MIDI do IAC Driver
   - Ajuste o mapeamento de notas conforme necessário:
     - Pad 0 → Nota 38 (Snare)
     - Pad 1 → Nota 36 (Kick)
     - Pad 2 → Nota 42 (Hi-Hat Fechado)
     - etc.
   - Clique em "Iniciar Tradutor"

3. No Addictive Drums 2:
   - Configure para receber MIDI do IAC Driver
   - Teste tocando nos pads do MicroDrum

## Mapeamento de Notas General MIDI para Bateria (Canal 10)

| Nota | Instrumento        |
|------|-------------------|
| 36   | Bass Drum (Kick)  |
| 38   | Snare Drum        |
| 40   | Snare Rim         |
| 42   | Hi-Hat Fechado    |
| 46   | Hi-Hat Aberto     |
| 41   | Tom 1 (Agudo)     |
| 43   | Tom 2 (Médio)     |
| 45   | Tom 3 (Grave)     |
| 49   | Crash Cymbal      |
| 51   | Ride Cymbal       |
| 57   | Crash Cymbal 2    |

## Solução Permanente

Para uma solução permanente, você pode:

1. **Usar o tradutor MIDI aprimorado**: Sempre execute o tradutor antes de usar o MicroDrum com o Addictive Drums 2.

2. **Modificar o firmware do Arduino**: Se você tiver acesso ao código-fonte do firmware do MicroDrum, pode corrigir a implementação:

   ```cpp
   // Em vez de:
   Serial.write(0xC0);
   Serial.write(0);  // Nota 0 para snare
   Serial.write(velocity);
   
   // Use:
   Serial.write(0x99);  // Note On no canal 10
   Serial.write(38);    // Nota 38 para snare
   Serial.write(velocity > 0 ? velocity : 64);  // Garantir velocidade não-zero
   ```

## Dicas para Configuração do Addictive Drums 2

1. **Verifique o canal MIDI**: Certifique-se de que o Addictive Drums 2 está configurado para receber no canal 10.

2. **Mapeamento MIDI**: No Addictive Drums 2, verifique se o mapeamento MIDI está configurado para o padrão General MIDI.

3. **Teste com notas individuais**: Use um teclado MIDI virtual para enviar notas específicas (como a nota 38) para verificar se o Addictive Drums 2 está respondendo corretamente.