# 🚀 Como Fazer Upload do Projeto para o GitHub

## Pré-requisitos

1. **Conta no GitHub**: Crie uma conta em [github.com](https://github.com) se ainda não tiver
2. **Git instalado**: Baixe e instale o Git de [git-scm.com](https://git-scm.com/)

## Passos para Upload

### 1. Configurar Git (primeira vez apenas)
```bash
git config --global user.name "Seu Nome"
git config --global user.email "seuemail@exemplo.com"
```

### 2. Inicializar Repositório Local
```bash
# No diretório do projeto (C:\Users\Rafael\Desktop\b2b)
git init
git add .
git commit -m "Initial commit: Sistema B2B completo"
```

### 3. Criar Repositório no GitHub
1. Acesse [github.com](https://github.com)
2. Clique em "New repository" (botão verde)
3. Nome do repositório: `sistema-b2b-leads`
4. Descrição: `Sistema completo para extração de dados B2B com filtros avançados e controle de leads`
5. Deixe como **Public** ou **Private** (sua escolha)
6. **NÃO** marque "Add a README file" (já temos um)
7. Clique em "Create repository"

### 4. Conectar Local com GitHub
```bash
# Substitua 'SEU_USUARIO' pelo seu nome de usuário do GitHub
git remote add origin https://github.com/SEU_USUARIO/sistema-b2b-leads.git
git branch -M main
git push -u origin main
```

### 5. Comandos Úteis para Futuras Atualizações
```bash
# Adicionar alterações
git add .

# Fazer commit
git commit -m "Descrição das alterações"

# Enviar para GitHub
git push
```

## 📁 Estrutura que Será Enviada

```
sistema-b2b-leads/
├── app.py                 # ✅ Aplicação Flask principal
├── create_test_db.py      # ✅ Gerador de banco de teste
├── requirements.txt       # ✅ Dependências Python
├── README.md             # ✅ Documentação completa
├── GITHUB_SETUP.md       # ✅ Este arquivo
├── .gitignore            # ✅ Arquivos a ignorar
├── templates/            # ✅ Interface web
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── filter.html
│   └── admin.html
└── data/
    └── empresas_teste.db # ⚠️ IGNORADO (muito grande)
```

## ⚠️ Importante

- O arquivo `empresas_teste.db` **NÃO** será enviado (está no .gitignore)
- Usuários que baixarem o projeto precisarão executar `python create_test_db.py` para criar o banco
- Arquivos de upload e logs também são ignorados por segurança

## 🎯 Benefícios do GitHub

- ✅ **Backup seguro** do seu código
- ✅ **Controle de versão** para rastrear mudanças
- ✅ **Colaboração** com outros desenvolvedores
- ✅ **Portfolio** profissional visível
- ✅ **Deploy automático** (GitHub Pages, Heroku, etc.)

## 🔧 Comandos Rápidos

```bash
# Status atual
git status

# Ver histórico
git log --oneline

# Criar nova branch
git checkout -b nova-funcionalidade

# Voltar para main
git checkout main

# Merge de branch
git merge nova-funcionalidade
```

## 📞 Problemas Comuns

### Erro de autenticação
- Use Personal Access Token em vez de senha
- GitHub Settings → Developer settings → Personal access tokens

### Arquivo muito grande
- Está coberto pelo .gitignore
- Use Git LFS se necessário

### Primeira vez com Git
- Tutorial oficial: [git-scm.com/docs/gittutorial](https://git-scm.com/docs/gittutorial)

---

**Depois do upload, seu projeto estará disponível em:**
`https://github.com/SEU_USUARIO/sistema-b2b-leads`
