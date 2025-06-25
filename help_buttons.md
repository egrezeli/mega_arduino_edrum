# Guia de Botões do Mega Arduino eDrum

## Botões Principais

### GET ALL (↑)
- **Função**: Recebe todas as configurações do pad selecionado do Arduino para a interface
- **Quando usar**: Para ver as configurações atuais armazenadas no Arduino
- **Direção do fluxo de dados**: Arduino → Interface

### SET ALL (↓)
- **Função**: Envia todas as configurações do pad selecionado da interface para o Arduino
- **Quando usar**: Após modificar configurações na interface e querer aplicá-las ao Arduino
- **Direção do fluxo de dados**: Interface → Arduino

## Botões Individuais

Cada parâmetro tem dois botões associados:

### Botões GET (↑)
- **Função**: Recebem um parâmetro específico do Arduino para a interface
- **Exemplo**: O botão GET para "Type" recebe apenas o tipo do pad do Arduino

### Botões SET (↓)
- **Função**: Enviam um parâmetro específico da interface para o Arduino
- **Exemplo**: O botão SET para "Note" envia apenas a nota MIDI para o Arduino

## Dicas de Uso

1. Use **GET ALL** quando conectar pela primeira vez ou quando quiser sincronizar a interface com o Arduino
2. Use **SET ALL** após fazer várias alterações na interface
3. Use os botões individuais quando quiser atualizar apenas um parâmetro específico
4. Marque a opção **Save** se quiser que as configurações sejam salvas na EEPROM do Arduino (permanentes após desligar)

## Parâmetros Importantes

- **Type**: Tipo de sensor (Piezo, Switch, HHC, Disabled)
- **Note**: Nota MIDI que será enviada quando o pad for tocado
- **Threshold**: Sensibilidade do pad (valor mínimo para detecção)
- **Gain**: Amplificação do sinal do sensor
- **Xtalk**: Redução de interferência entre pads próximos
- **Xtalkgroup**: Grupo de pads que compartilham configurações de cross-talk