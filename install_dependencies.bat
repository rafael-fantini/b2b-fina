@echo off
chcp 65001 >nul
echo 🚀 Instalando dependências do Sistema B2B...
echo ================================================

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Instale Python 3.8+ primeiro.
    echo 📥 Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python encontrado:
python --version

REM Verificar se pip está instalado
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip não encontrado. Instalando...
    python -m ensurepip --upgrade
)

echo ✅ pip encontrado:
pip --version

REM Atualizar pip
echo 🔄 Atualizando pip...
python -m pip install --upgrade pip

REM Criar ambiente virtual se não existir
if not exist "venv" (
    echo 🔧 Criando ambiente virtual...
    python -m venv venv
)

REM Ativar ambiente virtual
echo 🔧 Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Verificar se estamos no ambiente virtual
if "%VIRTUAL_ENV%"=="" (
    echo ❌ Falha ao ativar ambiente virtual
    pause
    exit /b 1
)

echo ✅ Ambiente virtual ativado: %VIRTUAL_ENV%

REM Limpar cache do pip
echo 🧹 Limpando cache do pip...
pip cache purge

REM Instalar dependências uma por uma para melhor controle
echo 📦 Instalando dependências Python...

echo    - Instalando Flask...
pip install Flask==2.3.3

echo    - Instalando Werkzeug...
pip install Werkzeug==2.3.7

echo    - Instalando Jinja2...
pip install Jinja2==3.1.2

echo    - Instalando SQLAlchemy...
pip install SQLAlchemy==2.0.21

echo    - Instalando Flask-SQLAlchemy...
pip install Flask-SQLAlchemy==3.0.5

echo    - Instalando pandas...
pip install pandas==2.1.1

echo    - Instalando numpy...
pip install numpy==1.25.2

echo    - Instalando openpyxl...
pip install openpyxl==3.1.2

echo    - Instalando python-dateutil...
pip install python-dateutil==2.8.2

echo    - Instalando Faker...
pip install Faker==19.6.2

echo    - Instalando python-dotenv...
pip install python-dotenv==1.0.0

REM Verificar instalação
echo 🔍 Verificando instalação...
python -c "import flask; print(f'✅ Flask {flask.__version__} instalado com sucesso!')"
python -c "import pandas; print(f'✅ Pandas {pandas.__version__} instalado com sucesso!')"
python -c "import sqlalchemy; print(f'✅ SQLAlchemy {sqlalchemy.__version__} instalado com sucesso!')"

REM Gerar requirements.txt atualizado
echo 📝 Gerando requirements.txt atualizado...
pip freeze > requirements_installed.txt

echo ================================================
echo 🎉 Instalação concluída com sucesso!
echo 📁 Ambiente virtual: %VIRTUAL_ENV%
echo 📋 Dependências instaladas: requirements_installed.txt
echo.
echo 🚀 Para ativar o ambiente virtual:
echo    venv\Scripts\activate.bat
echo.
echo 🌐 Para executar a aplicação:
echo    python app.py
echo.
echo 🔧 Para instalar dependências adicionais:
echo    pip install nome_do_pacote
echo.
pause
