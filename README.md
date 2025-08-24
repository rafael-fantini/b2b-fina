# Sistema B2B - Extração de Dados Empresariais

Sistema completo para extração e gerenciamento de dados B2B de empresas brasileiras, com interface web moderna, sistema de filtros avançados e controle de licenciamento por product keys.

## ✨ Funcionalidades

### 🔐 Sistema de Autenticação
- Login/Cadastro de usuários
- Sistema de Product Keys para licenciamento
- Controle de leads disponíveis (1.000/2.000/10.000/50.000)
- Painel administrativo completo

### 🗃️ Banco de Dados
- Estrutura compatível com dados da Receita Federal
- Suporte a arquivos SQLite (.db)
- Banco de teste com 1.500 empresas brasileiras
- Upload de novos bancos via painel admin

### 🔍 Sistema de Filtros Avançados
- Filtros por todos os campos disponíveis:
  - CNPJ Básico, Razão Social, Nome Fantasia
  - UF, Município, Telefone, Email
  - Situação Cadastral, Optante Simples
  - CNAE, Natureza Jurídica, Capital Social
  - E muito mais...
- Salvamento e reutilização de filtros
- Preview em tempo real dos resultados

### 📊 Exportação de Dados
- Formatos CSV e Excel (XLSX)
- Seleção personalizada de colunas
- Download direto dos arquivos
- Controle automático de consumo de leads

### 🎨 Interface Moderna
- Design responsivo e intuitivo
- Dashboard com estatísticas em tempo real
- Gráficos interativos com Chart.js
- Experiência otimizada para desktop e mobile

## 🚀 Instalação

### Pré-requisitos
- Python 3.7+
- Pip (gerenciador de pacotes Python)

### Passos de Instalação

1. **Clone ou baixe o projeto**
   ```bash
   cd sistema-b2b
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute o sistema**
   ```bash
   python app.py
   ```

4. **Acesse o sistema**
   - Abra seu navegador em: http://localhost:5000
   - **Login admin padrão:** admin / admin123

## 🎯 Como Usar

### Para Administradores

1. **Acesse o painel admin** (usuário: admin, senha: admin123)
2. **Gere Product Keys:**
   - Escolha a quantidade de leads (1k, 2k, 10k, 50k)
   - Defina quantas keys gerar
   - Distribua as keys para os usuários

3. **Configure o banco de dados:**
   - Use o banco de teste incluído, ou
   - Faça upload de um novo arquivo .db via "Abrir Explorer"

### Para Usuários

1. **Crie uma conta:**
   - Use uma Product Key válida para ativar
   - Faça login com suas credenciais

2. **Adicione mais leads:**
   - No dashboard, use a seção "Adicionar Mais Leads"
   - Digite uma nova Product Key válida
   - Os leads serão somados ao seu plano atual
   - Você pode usar múltiplas Product Keys

3. **Use o sistema de filtros:**
   - Acesse "Filtros" no menu principal
   - Configure os filtros desejados
   - Selecione as colunas para exportação
   - Visualize o preview dos resultados

4. **Exporte os dados:**
   - Escolha o formato (CSV ou Excel)
   - Clique em "Exportar Dados"
   - O arquivo será baixado automaticamente
   - Seus leads serão automaticamente decrementados

## 🏗️ Estrutura do Projeto

```
sistema-b2b/
├── app.py                 # Aplicação Flask principal
├── create_test_db.py      # Script para criar banco de teste
├── requirements.txt       # Dependências Python
├── README.md             # Este arquivo
├── templates/            # Templates HTML
│   ├── base.html         # Template base
│   ├── login.html        # Página de login
│   ├── register.html     # Página de cadastro
│   ├── dashboard.html    # Dashboard principal
│   ├── filter.html       # Sistema de filtros
│   └── admin.html        # Painel administrativo
├── data/                 # Banco de dados
│   └── empresas_teste.db # Banco SQLite de teste
└── uploads/              # Uploads de novos bancos
```

## 🗄️ Estrutura do Banco de Dados

O sistema utiliza a estrutura oficial da Receita Federal:

- **empresas**: Dados básicos das empresas
- **estabelecimento**: Informações de estabelecimentos
- **simples**: Status do Simples Nacional
- **socios**: Informações dos sócios
- **Tabelas de referência**: CNAEs, municípios, países, etc.

## 🔧 Configurações

### Product Keys Disponíveis
- **1.000 leads**: Plano Básico
- **2.000 leads**: Plano Standard  
- **10.000 leads**: Plano Professional
- **50.000 leads**: Plano Premium

### Campos Disponíveis para Filtro/Exportação
- CNPJ Básico, Ordem, DV e Completo
- Razão Social e Nome Fantasia
- Endereço completo (logradouro, número, bairro, CEP, UF)
- Telefones e email
- Situação cadastral e datas
- CNAE principal
- Status Simples Nacional e MEI
- Natureza jurídica
- Qualificação do responsável

## 🛡️ Segurança

- Senhas criptografadas com hash
- Controle de sessão
- Validação de product keys
- Proteção contra acesso não autorizado
- Logs de atividades

## 🎨 Tecnologias Utilizadas

- **Backend**: Flask (Python)
- **Frontend**: Bootstrap 5, Chart.js
- **Banco de Dados**: SQLite
- **Exportação**: Pandas, OpenPyXL
- **Dados Fictícios**: Faker

## 📞 Suporte

O sistema foi desenvolvido para ser intuitivo e fácil de usar. Para dúvidas:

1. Verifique este README
2. Use o usuário admin para configurações
3. Teste com o banco de dados incluído
4. Verifique os logs do Flask em caso de erros

## 🚀 Funcionalidades Avançadas

- **Dashboard com estatísticas em tempo real**
- **Gráficos de distribuição por estado**
- **Análise de optantes do Simples Nacional**
- **Sistema de filtros salvos**
- **Export rápido de empresas ativas**
- **Adição de múltiplas Product Keys** - Usuários podem somar leads de várias keys
- **Gerenciamento completo de usuários**
- **Reset de leads pelo admin**
- **Upload de bancos via explorer**

---

**Sistema B2B v1.0** - Desenvolvido com ❤️ para facilitar a extração de dados empresariais brasileiros.
