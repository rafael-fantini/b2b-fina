# 🔧 Guia de Solução de Problemas - Sistema B2B

## ❌ **Problema: Flask não instala**

### **Solução 1: Limpar ambiente virtual**
```bash
# Remover ambiente virtual existente
rm -rf venv/

# Criar novo ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate.bat  # Windows

# Atualizar pip
pip install --upgrade pip

# Instalar Flask especificamente
pip install Flask==2.3.3
```

### **Solução 2: Verificar versão do Python**
```bash
python3 --version
# Deve ser Python 3.8 ou superior

# Se for Python 2.x, use:
python3 -m pip install Flask
```

### **Solução 3: Instalar dependências do sistema (Ubuntu/Debian)**
```bash
sudo apt update
sudo apt install -y python3-dev build-essential libssl-dev libffi-dev
sudo apt install -y python3-pip python3-venv
```

### **Solução 4: Instalar dependências do sistema (CentOS/RHEL)**
```bash
sudo yum groupinstall -y "Development Tools"
sudo yum install -y python3-devel openssl-devel libffi-devel
sudo yum install -y python3-pip
```

## ❌ **Problema: Erro de compilação do pandas**

### **Solução: Instalar compiladores**
```bash
# Ubuntu/Debian
sudo apt install -y build-essential python3-dev

# CentOS/RHEL
sudo yum groupinstall -y "Development Tools"
sudo yum install -y python3-devel
```

## ❌ **Problema: Erro de permissão**

### **Solução: Usar ambiente virtual**
```bash
# NUNCA instale pacotes globalmente com sudo pip
# Sempre use ambiente virtual

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## ❌ **Problema: Conflito de versões**

### **Solução: Versões específicas**
```bash
# Remover versões conflitantes
pip uninstall flask flask-sqlalchemy werkzeug -y

# Instalar versões específicas
pip install Flask==2.3.3
pip install Werkzeug==2.3.7
pip install Flask-SQLAlchemy==3.0.5
```

## ❌ **Problema: Erro de SSL/TLS**

### **Solução: Atualizar certificados**
```bash
# Ubuntu/Debian
sudo apt install -y ca-certificates
sudo update-ca-certificates

# CentOS/RHEL
sudo yum install -y ca-certificates
sudo update-ca-trust
```

## ❌ **Problema: Erro de proxy/firewall**

### **Solução: Configurar pip**
```bash
# Criar arquivo de configuração
mkdir ~/.pip
nano ~/.pip/pip.conf

# Adicionar configurações:
[global]
trusted-host = pypi.org pypi.python.org files.pythonhosted.org
```

## ❌ **Problema: Erro de memória insuficiente**

### **Solução: Aumentar swap**
```bash
# Criar arquivo de swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Tornar permanente
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## ❌ **Problema: Erro de dependências circulares**

### **Solução: Instalação sequencial**
```bash
# Instalar dependências base primeiro
pip install setuptools wheel

# Depois instalar pacotes principais
pip install Flask==2.3.3
pip install Werkzeug==2.3.7
pip install SQLAlchemy==2.0.21
pip install Flask-SQLAlchemy==3.0.5

# Por último, pacotes que dependem dos anteriores
pip install pandas==2.1.1
pip install openpyxl==3.1.2
```

## ❌ **Problema: Erro de arquitetura incompatível**

### **Solução: Verificar arquitetura**
```bash
# Verificar arquitetura do sistema
uname -m

# Verificar arquitetura do Python
python3 -c "import platform; print(platform.architecture())"

# Se for ARM64, pode precisar de versões específicas
pip install --only-binary=all pandas
```

## ❌ **Problema: Erro de cache corrompido**

### **Solução: Limpar cache**
```bash
# Limpar cache do pip
pip cache purge

# Limpar cache do pip global
pip cache purge --global

# Remover diretórios de cache
rm -rf ~/.cache/pip
rm -rf ~/.local/lib/python*/site-packages/
```

## ❌ **Problema: Erro de permissão no Windows**

### **Solução: Executar como administrador**
```cmd
# Executar PowerShell como administrador
# Ou executar cmd como administrador

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
venv\Scripts\activate.bat

# Instalar dependências
pip install -r requirements.txt
```

## ❌ **Problema: Erro de encoding no Windows**

### **Solução: Configurar encoding**
```cmd
# No cmd, antes de executar:
chcp 65001

# Ou usar PowerShell que já tem UTF-8 por padrão
```

## 🔍 **Verificação de Instalação**

### **Teste básico:**
```bash
# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate.bat  # Windows

# Testar importações
python -c "import flask; print('Flask OK')"
python -c "import pandas; print('Pandas OK')"
python -c "import sqlalchemy; print('SQLAlchemy OK')"
```

### **Teste da aplicação:**
```bash
# Executar aplicação
python app.py

# Deve mostrar:
# * Running on http://127.0.0.1:5000
# * Debug mode: on
```

## 📞 **Suporte Adicional**

Se nenhuma solução funcionar:

1. **Verificar logs de erro** completos
2. **Verificar versão do Python** e pip
3. **Verificar sistema operacional** e arquitetura
4. **Verificar permissões** de usuário
5. **Verificar conexão** com PyPI

## 🚀 **Scripts Automatizados**

Use os scripts fornecidos:
- **Linux/Mac:** `install_dependencies.sh`
- **Windows:** `install_dependencies.bat`

Estes scripts resolvem automaticamente a maioria dos problemas comuns.
