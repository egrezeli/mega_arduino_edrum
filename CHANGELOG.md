# Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

## [1.1.0] - 2025-06-24

### Adicionado
- Botão "Resetar Monitor" para limpar todas as barras de progresso na aba Monitor
- Tooltips melhorados para os botões GET/SET explicando sua função
- Caixas de diálogo informativas após operações importantes
- Documentação detalhada para configuração da caixa dual-zone com um piezo
- Documentação para configurações otimizadas para diferentes técnicas de bateria
- Correção para evitar que pads desabilitados apareçam no monitor

### Modificado
- Melhorada a função `handle_updateMonitor` para garantir que pads desabilitados tenham valor zero
- Modificada a função `disableAllPins` para também resetar o monitor

### Corrigido
- Corrigido bug que fazia pads desabilitados aparecerem no monitor
- Corrigido posicionamento de botões na interface

## [1.0.0] - 2025-05-15

### Adicionado
- Compatibilidade com Python 3 e PyQt5
- Interface gráfica melhorada e mais responsiva
- Suporte para sistemas operacionais modernos (Windows, macOS, Linux)
- Carregamento e salvamento automático de configurações
- Sincronização bidirecional com o Arduino (recebe e envia configurações)
- Botão para desabilitar todos os pinos de uma vez
- Tratamento de erros aprimorado
- Feedback visual para operações de longa duração
- Log's em tempo real na aba "Tool"
- Painel informativo de nota MIDI enviada na aba monitor

### Modificado
- Reescrita completa do código para Python 3
- Otimizações de latência para resposta mais rápida dos pads
- Comunicação serial otimizada para baixa latência
- Melhor organização do código e documentação

### Corrigido
- Diversos bugs da versão original
- Problemas de compatibilidade com sistemas operacionais modernos
- Problemas de latência e responsividade