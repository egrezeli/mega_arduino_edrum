# Correção do Erro QVector<int> no MicroDrum Config Tool

Este documento explica como foi corrigido o erro "Cannot queue arguments of type 'QVector<int>'" no MicroDrum Config Tool.

## Problema

O erro ocorre quando o PyQt5 tenta passar um objeto `QVector<int>` através de uma conexão de sinal/slot entre threads, mas o tipo não está registrado no sistema de meta-objetos do Qt:

```
QObject::connect: Cannot queue arguments of type 'QVector<int>'
(Make sure 'QVector<int>' is registered using qRegisterMetaType().)
```

Outro erro relacionado é:
```
Erro ao processar comando SysEx: 15
```

## Causa

O problema ocorre porque:

1. O PyQt5 usa `QVector<int>` internamente para representar tuplas de inteiros
2. Quando esses dados são passados entre threads através de sinais/slots, o Qt precisa saber como serializar e deserializar o tipo
3. Em algumas versões do PyQt5, a função `qRegisterMetaType()` não está disponível ou não funciona corretamente

## Solução Implementada

Em vez de tentar registrar o tipo `QVector<int>`, modificamos o código para usar tipos básicos do Python que o PyQt5 já sabe como lidar:

1. Adicionamos comentários explicativos sobre o uso de tipos básicos:
   ```python
   # Usar sinais com tipos básicos para evitar problemas de compatibilidade
   updateMonitor = pyqtSignal(int,int,int)
   logMessage = pyqtSignal(str)
   ```

2. Modificamos a função `read_midi` para converter explicitamente para tipos básicos:
   ```python
   # Usar list() para evitar problemas com QVector<int>
   data = list(struct.unpack("B"*len(rxData), rxData))
   ```

3. Garantimos que os valores passados para o sinal `updateMonitor` sejam do tipo `int`:
   ```python
   # Usar tipos básicos para evitar problemas com QVector<int>
   self.updateMonitor.emit(int(cmd), int(note), int(vel))
   ```

4. Usamos `list()` em vez de fatias diretas para evitar tipos desconhecidos:
   ```python
   # Usar list() para evitar problemas com QVector<int>
   hash_value = self.getPearsonHash(list(data[2:4]))
   ```

## Benefícios da Solução

1. **Compatibilidade**: Funciona em todas as versões do PyQt5, independentemente da disponibilidade de `qRegisterMetaType()`
2. **Simplicidade**: Não requer registro de tipos personalizados
3. **Robustez**: Evita erros de serialização entre threads

## Alternativas Consideradas

1. **Registrar o tipo com `qRegisterMetaType()`**: Não funcionou porque a função não está disponível em todas as versões do PyQt5
2. **Usar um script separado para registrar o tipo**: Não funcionou pelo mesmo motivo
3. **Modificar o sistema de sinais/slots**: Seria uma mudança muito invasiva no código

## Conclusão

A solução implementada resolve o problema de forma simples e robusta, garantindo que o MicroDrum Config Tool funcione corretamente em diferentes versões do PyQt5 e sistemas operacionais.