#!/bin/bash

echo "🚀 Instalando dependências do Sistema B2B..."
echo "================================================"

# Verificar se Python3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instalando..."
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3 python3-pip
    else
        echo "❌ Sistema não suportado. Instale Python3 manualmente."
        exit 1
    fi
fi

echo "✅ Python3 encontrado: $(python3 --version)"

# Verificar se pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Instalando..."
    if command -v apt &> /dev/null; then
        sudo apt install -y python3-pip
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3-pip
    fi
fi

echo "✅ pip3 encontrado: $(pip3 --version)"

# Atualizar pip
echo "🔄 Atualizando pip..."
python3 -m pip install --upgrade pip

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "🔧 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Verificar se estamos no ambiente virtual
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Falha ao ativar ambiente virtual"
    exit 1
fi

echo "✅ Ambiente virtual ativado: $VIRTUAL_ENV"

# Instalar dependências do sistema (Ubuntu/Debian)
if command -v apt &> /dev/null; then
    echo "🔄 Instalando dependências do sistema..."
    sudo apt update
    sudo apt install -y python3-dev build-essential libssl-dev libffi-dev
    sudo apt install -y libxml2-dev libxslt1-dev zlib1g-dev
fi

# Instalar dependências do sistema (CentOS/RHEL)
if command -v yum &> /dev/null; then
    echo "🔄 Instalando dependências do sistema..."
    sudo yum groupinstall -y "Development Tools"
    sudo yum install -y python3-devel openssl-devel libffi-devel
    sudo yum install -y libxml2-devel libxslt-devel zlib-devel
fi

# Limpar cache do pip
echo "🧹 Limpando cache do pip..."
pip cache purge

# Instalar dependências uma por uma para melhor controle
echo "📦 Instalando dependências Python..."

echo "   - Instalando Flask..."
pip install Flask==2.3.3

echo "   - Instalando Werkzeug..."
pip install Werkzeug==2.3.7

echo "   - Instalando Jinja2..."
pip install Jinja2==3.1.2

echo "   - Instalando SQLAlchemy..."
pip install SQLAlchemy==2.0.21

echo "   - Instalando Flask-SQLAlchemy..."
pip install Flask-SQLAlchemy==3.0.5

echo "   - Instalando pandas..."
pip install pandas==2.1.1

echo "   - Instalando numpy..."
pip install numpy==1.25.2

echo "   - Instalando openpyxl..."
pip install openpyxl==3.1.2

echo "   - Instalando python-dateutil..."
pip install python-dateutil==2.8.2

echo "   - Instalando Faker..."
pip install Faker==19.6.2

echo "   - Instalando gunicorn..."
pip install gunicorn==21.2.0

echo "   - Instalando python-dotenv..."
pip install python-dotenv==1.0.0

# Verificar instalação
echo "🔍 Verificando instalação..."
python3 -c "import flask; print(f'✅ Flask {flask.__version__} instalado com sucesso!')"
python3 -c "import pandas; print(f'✅ Pandas {pandas.__version__} instalado com sucesso!')"
python3 -c "import sqlalchemy; print(f'✅ SQLAlchemy {sqlalchemy.__version__} instalado com sucesso!')"

# Gerar requirements.txt atualizado
echo "📝 Gerando requirements.txt atualizado..."
pip freeze > requirements_installed.txt

echo "================================================"
echo "🎉 Instalação concluída com sucesso!"
echo "📁 Ambiente virtual: $VIRTUAL_ENV"
echo "📋 Dependências instaladas: requirements_installed.txt"
echo ""
echo "🚀 Para ativar o ambiente virtual:"
echo "   source venv/bin/activate"
echo ""
echo "🌐 Para executar a aplicação:"
echo "   python app.py"
echo ""
echo "🔧 Para instalar dependências adicionais:"
echo "   pip install nome_do_pacote"
