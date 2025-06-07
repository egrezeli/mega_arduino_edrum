# Configuração MIDI para MicroDrum Config Tool

Este guia explica como configurar o MicroDrum Config Tool para funcionar corretamente com o Addictive Drums 2 no macOS.

## Problema

O MicroDrum Config Tool envia mensagens MIDI em um formato que o Addictive Drums 2 não reconhece corretamente:
- Usa notas incorretas (ex: nota 0 para a snare em vez da nota 38)
- Pode enviar velocidade zero, que é interpretada como "note off"
- Usa um formato de mensagem não padrão

## Solução: MIDI Bridge

A MIDI Bridge (`midi_bridge.py`) é uma ferramenta que:
1. Intercepta as mensagens MIDI enviadas pelo MicroDrum Config Tool
2. Corrige as notas e velocidades
3. Envia as mensagens corrigidas para o Addictive Drums 2

## Configuração do IAC Driver

Para usar a MIDI Bridge, você precisa configurar dois barramentos IAC:

1. Abra "Configuração Áudio e MIDI" (Audio MIDI Setup)
2. Pressione `Cmd+2` para mostrar a janela "Estúdio MIDI"
3. Dê duplo clique no "IAC Driver"
4. Certifique-se de que a opção "Dispositivo está online" está marcada
5. Adicione dois barramentos:
   - "IAC Bus 1" (para o MicroDrum Config Tool)
   - "IAC Bus 2" (para o Addictive Drums 2)

## Como usar a MIDI Bridge

1. Execute a MIDI Bridge:
   ```bash
   ./midi_bridge.py
   ```

2. Configure:
   - **MIDI de Entrada**: Selecione "IAC Bus 1" (onde o MicroDrum Config Tool envia)
   - **MIDI de Saída**: Selecione "IAC Bus 2" (onde o Addictive Drums 2 recebe)
   - Clique em "Iniciar Bridge"

3. Configure o MicroDrum Config Tool:
   - Conecte o Arduino via USB
   - Habilite a porta serial
   - Na aba "Monitor", selecione "To MIDI"
   - Escolha "IAC Bus 1" na lista suspensa

4. Configure o Addictive Drums 2:
   - Configure para receber MIDI do "IAC Bus 2"
   - Certifique-se de que está configurado para o canal 10 (bateria)

## Fluxo de Dados

```
Arduino → MicroDrum Config Tool → IAC Bus 1 → MIDI Bridge → IAC Bus 2 → Addictive Drums 2
```

## Mapeamento de Notas

A MIDI Bridge mapeia automaticamente as notas do MicroDrum para o padrão General MIDI:

| Nota Original | Nota Mapeada | Instrumento        |
|--------------|--------------|-------------------|
| 0            | 38           | Snare Drum        |
| 1            | 36           | Bass Drum (Kick)  |
| 2            | 42           | Hi-Hat Fechado    |
| 3            | 46           | Hi-Hat Aberto     |
| 4            | 41           | Tom 1 (Agudo)     |
| 5            | 43           | Tom 2 (Médio)     |
| 6            | 45           | Tom 3 (Grave)     |
| 7            | 49           | Crash Cymbal      |
| 8            | 51           | Ride Cymbal       |

## Solução Alternativa

Se preferir não usar a MIDI Bridge, você pode usar o Tradutor MIDI Aprimorado (`midi_translator_enhanced.py`) diretamente com o Arduino, ignorando o MicroDrum Config Tool para a parte de monitoramento MIDI:

1. Use o MicroDrum Config Tool apenas para configurar os parâmetros do Arduino
2. Feche o MicroDrum Config Tool
3. Execute o Tradutor MIDI Aprimorado para monitorar o Arduino e enviar MIDI para o Addictive Drums 2

## Solução Permanente

Para uma solução permanente, seria necessário modificar o código-fonte do MicroDrum Config Tool para corrigir a implementação do protocolo MIDI.