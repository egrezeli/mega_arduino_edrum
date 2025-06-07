# Correções de Erros no MicroDrum Config Tool

Este documento descreve as correções aplicadas para resolver erros específicos no MicroDrum Config Tool.

## 1. Erro de QVector<int>

### Problema
```
QObject::connect: Cannot queue arguments of type 'QVector<int>'
(Make sure 'QVector<int>' is registered using qRegisterMetaType().)
```

Este erro ocorre porque o PyQt5 tenta passar um objeto `QVector<int>` através de uma conexão de sinal/slot entre threads, mas o tipo não está registrado no sistema de meta-objetos do Qt.

### Solução
Registrar o tipo `QVector<int>` usando a função `qRegisterMetaType()` antes de criar qualquer conexão de sinal/slot:

```python
from PyQt5.QtCore import QVector, qRegisterMetaType
qRegisterMetaType("QVector<int>")
```

Esta correção foi aplicada em:
- `main.py`
- `mainwindow.py`

## 2. Erro ao processar comando SysEx: 15

### Problema
```
Erro ao processar comando SysEx: 15
```

Este erro pode ocorrer durante a comunicação serial com o Arduino, especialmente ao processar mensagens SysEx.

### Possíveis causas
1. Mensagem SysEx incompleta ou malformada
2. Timeout na comunicação serial
3. Erro de buffer na leitura serial

### Solução
A correção do erro de `QVector<int>` deve resolver este problema, pois ele estava relacionado à forma como os dados eram processados entre threads.

## 3. Problemas com fontes ausentes

### Problema
```
qt.qpa.fonts: Populating font family aliases took 231 ms. Replace uses of missing font family "Monospace" with one that exists to avoid this cost.
```

### Solução
Substituir referências a fontes ausentes por fontes disponíveis no sistema:

```css
/* Substitui fontes ausentes por fontes disponíveis no macOS */
* {
    font-family: Helvetica, Arial, sans-serif;
}

/* Substitui a fonte Monospace por fontes monoespaçadas disponíveis no macOS */
QTextEdit, QPlainTextEdit {
    font-family: Menlo, Monaco, Courier, monospace;
}
```

Esta correção foi aplicada no arquivo `style.qss`.

## 4. Problemas de comunicação MIDI

### Problema
O MicroDrum Config Tool não estava enviando mensagens MIDI no formato correto para o Addictive Drums 2.

### Solução
Modificar o firmware do Arduino para:
1. Usar sempre o canal 10 (0x09 em base 0) para mensagens MIDI de bateria
2. Garantir que a velocidade nunca seja zero
3. Usar o formato correto de mensagens MIDI (Note On: 0x9n, Note Off: 0x8n)

Esta correção foi aplicada nos arquivos:
- `a_midi.ino`
- `c_pin.ino`