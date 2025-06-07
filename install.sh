#!/bin/bash

# Script de instalação para Mega Arduino eDrum

echo "Instalando Mega Arduino eDrum..."

# Verificar se o Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "Python 3 não encontrado. Por favor, instale o Python 3 antes de continuar."
    exit 1
fi

# Verificar se o pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "pip3 não encontrado. Por favor, instale o pip3 antes de continuar."
    exit 1
fi

# Instalar dependências
echo "Instalando dependências..."
pip3 install -r requirements.txt

# Verificar se a instalação foi bem-sucedida
if [ $? -ne 0 ]; then
    echo "Erro ao instalar dependências. Por favor, verifique as mensagens de erro acima."
    exit 1
fi

# Verificar sistema operacional
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Sistema macOS detectado."
    echo "Dica: Para usar com dispositivos MIDI virtuais no macOS:"
    echo "1. Abra 'Configuração Áudio e MIDI'"
    echo "2. Pressione Cmd+2 para mostrar o Estúdio MIDI"
    echo "3. Dê duplo clique no IAC Driver"
    echo "4. Marque 'Dispositivo está online'"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Sistema Linux detectado."
    echo "Dica: Para acessar portas seriais no Linux, você pode precisar adicionar seu usuário ao grupo 'dialout':"
    echo "sudo usermod -a -G dialout $USER"
    echo "Você precisará fazer logout e login novamente para que as alterações tenham efeito."
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "Sistema Windows detectado."
    echo "Dica: Para dispositivos MIDI virtuais no Windows, considere usar loopMIDI."
fi

echo "Instalação concluída com sucesso!"
echo "Para executar o programa, use: ./run.sh"

# Tornar o script run.sh executável
chmod +x run.sh

exit 0