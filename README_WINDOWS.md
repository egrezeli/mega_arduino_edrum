# Instruções de Instalação para Windows

## Instalação Automática (Recomendado)

Para facilitar a instalação no Windows, fornecemos um script de instalação automática que configura todo o ambiente necessário para executar o Mega Arduino eDrum.

### Como usar o instalador automático:

1. **Baixe** todo o conteúdo deste repositório para seu computador
2. **Localize** o arquivo `instalar_mega_arduino_edrum.bat` na pasta principal
3. **Clique duas vezes** neste arquivo para executá-lo
4. **Siga** as instruções na tela

O instalador automático irá:
- Verificar se o Python está instalado no seu sistema
- Baixar e instalar o Python 3.10 se necessário
- Instalar todas as bibliotecas necessárias
- Criar um atalho na área de trabalho
- Oferecer a opção de iniciar o programa imediatamente

**Importante:** Execute este instalador **antes** de tentar usar o Mega Arduino eDrum pela primeira vez.

## Instalação Manual (Avançado)

Se preferir instalar manualmente, você precisará:

1. Instalar o Python 3.6 ou superior
2. Instalar as dependências:
   ```
   pip install PyQt5 pyserial python-rtmidi psutil
   ```
3. Executar o programa:
   ```
   python main.py
   ```

## Requisitos de Sistema

- Windows 7, 8, 10 ou 11
- 100 MB de espaço em disco para instalação
- Conexão com a Internet (apenas para instalação)
- Porta USB para conectar o Arduino

## Problemas Comuns

Se encontrar problemas durante a instalação:
- Certifique-se de executar o instalador como administrador
- Verifique se tem conexão com a Internet

Para mais informações, consulte o arquivo [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).