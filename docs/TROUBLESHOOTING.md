# Solução de Problemas

Este documento fornece soluções para problemas comuns que você pode encontrar ao usar o Mega Arduino eDrum.

## Problemas de Conexão Serial

### O Arduino não é detectado

- Verifique se o cabo USB está conectado corretamente
- Certifique-se de que o driver do Arduino está instalado
- Tente uma porta USB diferente
- Reinicie o computador com o Arduino conectado

### Erro ao abrir a porta serial

- Verifique se outro programa não está usando a porta serial
- Feche outros programas que possam estar usando a porta
- Reinicie o Arduino desconectando e reconectando o cabo USB

## Problemas de MIDI

### Nenhuma porta MIDI disponível

- Instale um driver de MIDI virtual como loopMIDI (Windows) ou IAC Driver (macOS)
- Verifique se o python-rtmidi foi instalado corretamente
- Reinicie o aplicativo após instalar drivers MIDI

### Mensagens MIDI não são recebidas

- Verifique se a porta MIDI correta está selecionada
- Certifique-se de que o Arduino está enviando dados MIDI
- Teste com um monitor MIDI externo para verificar se os sinais estão sendo enviados

## Problemas de Interface

### A interface não responde

- Verifique se o programa não está ocupado processando comandos
- Reinicie o aplicativo
- Verifique o uso de CPU e memória do sistema

### Botões ou controles não funcionam

- Verifique se a conexão serial está ativa
- Reinicie o aplicativo
- Verifique se o Arduino está respondendo a comandos

## Problemas de Configuração

### Configurações não são salvas

- Verifique as permissões de escrita no diretório do aplicativo
- Certifique-se de que o arquivo pins.ini não está marcado como somente leitura
- Verifique se há espaço disponível no disco

### Configurações não são carregadas do Arduino

- Verifique se o Arduino está programado com o firmware correto
- Certifique-se de que a comunicação serial está funcionando
- Tente reiniciar o Arduino e o aplicativo

## Problemas Específicos

### Erro QVector<int>

Este erro está relacionado ao registro de tipos no PyQt5. Foi corrigido na versão atual, mas se persistir:

1. Verifique se está usando a versão mais recente do PyQt5
2. Tente reinstalar o PyQt5 com `pip install --upgrade PyQt5`

### Funcionalidades FluidSynth ou SFZ

Estas funcionalidades não foram completamente testadas. Se encontrar problemas:

1. Verifique se as bibliotecas necessárias estão instaladas
2. Use a opção MIDI padrão que é mais estável
3. Reporte o problema para que possamos melhorar estas funcionalidades