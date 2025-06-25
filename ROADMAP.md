# Roadmap - Mega Arduino eDrum

Este documento apresenta as melhorias planejadas e sugeridas para futuras versões do Mega Arduino eDrum.

## Próximas Melhorias Planejadas

### Interface e Usabilidade
- [ ] **Modo Escuro** - Adicionar tema escuro para uso em ambientes com pouca luz
- [ ] **Perfis de Configuração** - Permitir salvar/carregar múltiplos perfis para diferentes kits
- [ ] **Assistente de Configuração** - Wizard para configuração inicial passo a passo
- [ ] **Visualização em Tempo Real** - Gráfico visual do sinal dos pads em tempo real

### Funcionalidades
- [ ] **Editor de Curvas** - Interface gráfica para criar curvas de velocidade personalizadas
- [ ] **Mapeamento MIDI Avançado** - Suporte para mapeamentos complexos (ex: diferentes notas baseadas na velocidade)
- [ ] **Calibração Automática** - Ferramenta para calibrar automaticamente threshold e gain
- [ ] **Suporte a Positional Sensing** - Detecção da posição da batida no pad (centro vs. borda)

### Técnico
- [ ] **Suporte a MIDI 2.0** - Implementar o novo protocolo MIDI para maior resolução
- [ ] **Exportação/Importação JSON** - Formato mais moderno para configurações
- [ ] **Atualizador de Firmware** - Interface para atualizar o firmware do Arduino
- [ ] **Suporte a VST** - Integração direta com plugins VST de bateria

### Documentação
- [ ] **Vídeos Tutoriais** - Tutoriais em vídeo integrados na aplicação
- [ ] **Exemplos de Configuração** - Biblioteca de configurações para kits populares
- [ ] **Guia de Solução de Problemas** - Ferramenta de diagnóstico interativa

### Comunidade
- [ ] **Compartilhamento de Configurações** - Plataforma para compartilhar configurações entre usuários
- [ ] **Fórum Integrado** - Acesso direto à comunidade para suporte

## Prioridades para a Próxima Versão (v1.2.0)

1. Modo Escuro
2. Perfis de Configuração
3. Editor de Curvas
4. Exemplos de Configuração

## Como Contribuir

Se você deseja contribuir com alguma dessas melhorias ou sugerir novas funcionalidades:

1. Verifique as [Issues](https://github.com/seu-usuario/mega_arduino_edrum/issues) para ver se a funcionalidade já está sendo discutida
2. Crie uma nova issue descrevendo sua sugestão ou a melhoria que deseja implementar
3. Faça um fork do repositório e trabalhe na branch `dev`
4. Envie um Pull Request quando a funcionalidade estiver pronta

## Notas de Implementação

- Todas as novas funcionalidades devem ser desenvolvidas na branch `dev`
- Mantenha a compatibilidade com versões anteriores sempre que possível
- Documente todas as novas funcionalidades
- Adicione testes para novas funcionalidades quando aplicável