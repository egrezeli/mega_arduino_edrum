# Ferramenta de Configuração MicroDrum

Esta é uma ferramenta de configuração Python para o projeto MicroDrum/MicroMegaDrum.

## Requisitos

- Python 3.x
- PyQt5
- pyserial
- python-rtmidi
- numpy

## Instalação

### Método Automático

1. Execute o script de instalação:

```bash
./install.sh
```

### Método Manual

1. Instale as dependências:

```bash
pip3 install pyqt5 pyserial python-rtmidi numpy
```

2. Converta o arquivo UI para Python:

```bash
pyuic5 microdrum.ui -o ui_microdrum.py
```

## Execução

Para executar a ferramenta de configuração:

```bash
python3 main.py
```

## Uso

1. Conecte seu módulo MicroDrum/MicroMegaDrum via USB
2. Selecione a porta serial correta na interface
3. Clique em "Conectar"
4. Configure os parâmetros dos pads conforme necessário
5. Use os botões "Upload" e "Download" para transferir configurações entre o computador e o módulo

## Solução de Problemas

- Se a interface não carregar corretamente, verifique se o arquivo `microdrum.ui` está presente
- Para problemas de conexão serial, verifique se o módulo está conectado e a porta correta está selecionada
- Para problemas com MIDI, verifique se o dispositivo MIDI está configurado corretamente no sistema

## Adaptações

Esta versão foi adaptada para Python 3 e PyQt5 a partir do código original que usava Python 2 e PyQt4.