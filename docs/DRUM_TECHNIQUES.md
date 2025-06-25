# Configurações para Técnicas de Bateria

Este guia fornece configurações otimizadas para diferentes técnicas de bateria no Mega Arduino eDrum.

## Rufos na Caixa

Para conseguir rufos rápidos e precisos na caixa, é necessário ajustar os parâmetros para permitir detecção rápida de batidas consecutivas.

### Configuração Recomendada para Rufos:

```
Snare Head;0;38;15;5;20;15;30;0;110;20;1;9
```

- **Threshold**: 15 (baixo para detectar batidas leves)
- **Scantime**: 5 (rápido para detectar o pico do sinal)
- **Masktime**: 20 (curto para permitir batidas consecutivas rápidas)
- **Retrigger**: 15 (reduzido para minimizar o tempo entre batidas)
- **Gain**: 30 (amplificado para melhor detecção de batidas leves)

### Explicação dos Parâmetros:

- **Threshold**: Determina quão forte deve ser a batida para ser detectada. Valores mais baixos permitem detectar batidas mais leves, essenciais para rufos.
- **Scantime**: Tempo em que o sistema busca o pico do sinal após detectar uma batida. Valores mais baixos permitem detecção mais rápida.
- **Masktime**: Período em que novas batidas são ignoradas após uma detecção. Valores mais baixos permitem batidas consecutivas mais rápidas.
- **Retrigger**: Tempo mínimo entre batidas consecutivas. Valores mais baixos permitem rufos mais rápidos.
- **Gain**: Amplificação do sinal. Valores mais altos amplificam batidas leves, útil para rufos.

## Técnicas de Chimbal (Hi-Hat)

Para controle preciso do chimbal, incluindo técnicas como "chick" e "splash", ajuste os parâmetros do controlador de chimbal (HHC).

### Configuração Recomendada para Hi-Hat:

```
HHC;2;4;10;10;30;30;20;0;110;0;0;9
```

- **Type**: HHC (2)
- **Note**: 4 (CC#4 para controle contínuo)
- **Threshold**: 10 (sensibilidade média)

### Notas para Hi-Hat:
- **Aberto**: 46
- **Semi-aberto**: 23
- **Fechado**: 22
- **Pedal (chick)**: 44

## Técnicas de Bumbo (Kick)

Para técnicas de bumbo como "heel-toe" ou batidas duplas rápidas, use estas configurações:

```
Kick;0;36;20;5;25;20;25;0;110;0;2;9
```

- **Threshold**: 20 (médio para evitar disparos falsos)
- **Scantime**: 5 (rápido para detecção precisa)
- **Masktime**: 25 (curto para permitir batidas rápidas)
- **Retrigger**: 20 (reduzido para técnicas de batida dupla)
- **Gain**: 25 (amplificado para melhor resposta)

## Técnicas de Prato (Cymbal)

Para técnicas como "choke" (abafamento) em pratos, use estas configurações:

### Configuração para Prato com Choke:

```
Crash Bow;0;49;25;10;30;30;20;0;110;0;3;9
Crash Edge;0;55;25;10;30;30;20;0;110;0;3;9
Crash Choke;1;80;20;10;30;30;20;0;110;0;3;9
```

- **Type**: Piezo (0) para o prato, Switch (1) para o choke
- **Note**: 49/55 para o prato, 80 para o choke
- **XtalkGroup**: Mesmo grupo (3) para todos os componentes do prato

## Dicas Gerais

1. **Ajuste Gradual**: Faça pequenos ajustes e teste após cada alteração
2. **Balanceamento**: Encontre o equilíbrio entre sensibilidade e prevenção de disparos falsos
3. **Salve Configurações**: Sempre marque a opção "Save" para salvar na EEPROM do Arduino
4. **Perfis**: Crie diferentes arquivos pins.ini para diferentes estilos de tocar
5. **Teste em Contexto**: Teste suas configurações tocando músicas reais, não apenas batidas isoladas