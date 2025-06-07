# MicroDrum Config Tool - Adaptações para macOS

Este documento descreve as modificações necessárias para executar o MicroDrum Config Tool no macOS com Python 3.

## Modificações Realizadas

### 1. Atualização para Python 3 e PyQt5

O código original foi escrito para Python 2 e PyQt4. As seguintes alterações foram feitas:

- Substituição de importações PyQt4 por PyQt5
- Adição de importação de QtWidgets (separado do QtGui no PyQt5)
- Correção da sintaxe de exceções (de `raise ImportError, "mensagem"` para `raise ImportError("mensagem")`)
- Correção de indentação (substituição de tabs por espaços)

### 2. Adaptação do módulo MIDI

- Substituição de `rtmidi_python` por `python-rtmidi`
- Adição de compatibilidade com a nova API do rtmidi:
  ```python
  midi_out = rtmidi.MidiOut()
  midi_out.ports = []
  port_count = midi_out.get_port_count()
  for i in range(port_count):
      midi_out.ports.append(midi_out.get_port_name(i))
  ```

### 3. Tratamento de erros para FluidSynth

- Adição de uma classe dummy para quando o FluidSynth não está disponível
- Tratamento de exceções SyntaxError para compatibilidade com Python 3

### 4. Correções de manipulação de bytes e strings

- Adaptação para o tratamento de bytes em Python 3
- Codificação explícita de strings para bytes ao salvar em estruturas C
- Decodificação de bytes para strings ao exibir na interface

### 5. Script de execução automatizado

Criação de um script `run.sh` que:
- Verifica se o módulo rtmidi está instalado
- Instala automaticamente se necessário
- Executa o programa

## Requisitos

- Python 3.x
- PyQt5
- python-rtmidi
- pyserial

## Instalação

```bash
# Instalar dependências
pip3 install pyqt5 pyserial python-rtmidi

# Executar o programa
./run.sh
```

## Problemas Conhecidos

1. **Fonte ausente**: O aviso "Replace uses of missing font family 'MS Shell Dlg 2'" é apenas informativo e não afeta a funcionalidade.

2. **FluidSynth**: Se você precisar de suporte a FluidSynth, instale-o separadamente:
   ```bash
   brew install fluid-synth
   pip3 install pyfluidsynth
   ```

3. **Permissões de porta serial**: Pode ser necessário conceder permissões para acessar portas seriais no macOS.

## Notas Adicionais

- O código foi adaptado para funcionar sem dependências opcionais (como FluidSynth)
- A interface foi mantida o mais próxima possível da original
- As funcionalidades principais (configuração de pads, comunicação MIDI e serial) foram preservadas