# Guia de Deploy - Sistema de Leads

Este guia detalha o processo completo de deploy do sistema no Google Cloud Platform com Firebase.

## Visão Geral da Arquitetura

- **Frontend**: Hospedado no Firebase Hosting
- **Backend**: Google App Engine (Python/Flask)
- **Banco de Dados**: Google Cloud SQL (MySQL)
- **Storage**: Google Cloud Storage (para uploads)

## Pré-requisitos

1. Conta Google Cloud com billing ativado
2. Google Cloud CLI instalado
3. Firebase CLI instalado
4. Python 3.11 instalado localmente
5. Git configurado

## Passo 1: Configurar Projeto GCP

### 1.1 Criar projeto

```bash
# Criar novo projeto
gcloud projects create seu-projeto-id --name="Sistema de Leads"

# Definir como projeto atual
gcloud config set project seu-projeto-id

# Ativar billing (necessário via Console)
```

### 1.2 Habilitar APIs necessárias

```bash
# Habilitar todas as APIs necessárias
gcloud services enable \
  appengine.googleapis.com \
  sqladmin.googleapis.com \
  compute.googleapis.com \
  vpcaccess.googleapis.com \
  cloudbuild.googleapis.com \
  firebase.googleapis.com
```

## Passo 2: Configurar Cloud SQL

Siga o guia detalhado em [CLOUD_SQL_SETUP.md](./CLOUD_SQL_SETUP.md)

Resumo:
```bash
# Criar instância MySQL
gcloud sql instances create sistema-leads-db \
  --database-version=MYSQL_8_0 \
  --tier=db-f1-micro \
  --region=us-central1

# Criar database
gcloud sql databases create sistema_db --instance=sistema-leads-db
```

## Passo 3: Configurar App Engine

### 3.1 Inicializar App Engine

```bash
# Criar app (escolha a mesma região do Cloud SQL)
gcloud app create --region=us-central1
```

### 3.2 Criar VPC Connector

```bash
gcloud compute networks vpc-access connectors create vpc-connector \
  --region=us-central1 \
  --subnet-mode=auto
```

## Passo 4: Preparar aplicação para deploy

### 4.1 Configurar variáveis de ambiente

```bash
# Copiar exemplo
cp .env.example .env

# Editar .env com suas configurações
nano .env
```

Configurações importantes:
- `SECRET_KEY`: Gere uma chave segura
- `DB_USER` e `DB_PASS`: Credenciais do Cloud SQL
- `INSTANCE_CONNECTION_NAME`: formato projeto:região:instância

### 4.2 Atualizar arquivos de configuração

```bash
# Atualizar app.yaml
sed -i "s/YOUR_PROJECT_ID/seu-projeto-id/g" app.yaml
sed -i "s/YOUR_REGION/us-central1/g" app.yaml

# Atualizar .firebaserc
sed -i "s/your-project-id/seu-projeto-id/g" .firebaserc
```

## Passo 5: Deploy

### 5.1 Deploy automático

```bash
# Executar script de deploy
./deploy.sh
```

### 5.2 Deploy manual

#### Backend (App Engine)

```bash
# Copiar arquivo de produção
cp app_production.py main.py

# Deploy
gcloud app deploy

# Limpar
rm main.py
```

#### Frontend (Firebase)

```bash
# Login no Firebase
firebase login

# Selecionar projeto
firebase use seu-projeto-id

# Deploy hosting
firebase deploy --only hosting
```

## Passo 6: Configuração pós-deploy

### 6.1 Verificar aplicação

```bash
# Abrir aplicação
gcloud app browse

# Ver logs
gcloud app logs tail -s default
```

### 6.2 Criar primeiro usuário admin

1. Acesse https://seu-projeto-id.appspot.com
2. Clique em "Registrar"
3. O primeiro usuário criado será automaticamente admin

### 6.3 Configurar domínio customizado (opcional)

```bash
# Mapear domínio
gcloud app domain-mappings create seu-dominio.com

# Seguir instruções para configurar DNS
```

## Passo 7: Monitoramento e Manutenção

### 7.1 Configurar alertas

No Console GCP:
1. Navegue para Monitoring
2. Crie alertas para:
   - Erros 5xx > 1%
   - Latência > 1000ms
   - CPU Cloud SQL > 80%

### 7.2 Backup regular

```bash
# Configurar backup automático do Cloud SQL
gcloud sql instances patch sistema-leads-db \
  --backup-start-time=03:00
```

### 7.3 Logs e debugging

```bash
# Ver logs em tempo real
gcloud app logs tail -s default

# Ver logs específicos
gcloud logging read "resource.type=gae_app" --limit=50

# SSH para instância (debugging)
gcloud app instances ssh --service=default --version=VERSION_ID
```

## Troubleshooting

### Erro 500 no App Engine

1. Verifique logs: `gcloud app logs tail`
2. Comum: variáveis de ambiente faltando
3. Solução: Configure no app.yaml ou Console

### Erro de conexão com Cloud SQL

1. Verifique INSTANCE_CONNECTION_NAME
2. Confirme VPC Connector está ativo
3. Teste conexão local com Cloud SQL Proxy

### Deploy falha

1. Verifique quota do projeto
2. Confirme billing está ativo
3. Verifique permissões da service account

## Custos estimados

- App Engine (F2): ~$50/mês
- Cloud SQL (micro): ~$15/mês
- Storage: ~$5/mês
- Total: ~$70-100/mês para uso moderado

## Scripts úteis

### Atualizar aplicação

```bash
#!/bin/bash
# update_app.sh
git pull origin main
gcloud app deploy --quiet
```

### Backup manual

```bash
#!/bin/bash
# backup.sh
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
gcloud sql backups create --instance=sistema-leads-db
gcloud sql export sql sistema-leads-db gs://seu-bucket/backups/backup_$TIMESTAMP.sql
```

### Rollback

```bash
# Listar versões
gcloud app versions list

# Promover versão anterior
gcloud app versions migrate VERSION_ID
```

## Checklist de Segurança

- [ ] SECRET_KEY forte e única
- [ ] HTTPS forçado (configurado por padrão)
- [ ] Firewall do Cloud SQL configurado
- [ ] Backup automático ativado
- [ ] Monitoramento configurado
- [ ] Rate limiting implementado
- [ ] CORS configurado corretamente
- [ ] Logs de auditoria ativados

## Suporte

Para problemas:
1. Verifique logs primeiro
2. Consulte documentação GCP
3. Use `gcloud` comandos de debug
4. Abra issue no repositório