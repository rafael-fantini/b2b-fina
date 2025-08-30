# Configuração do Google Cloud SQL

Este documento descreve como configurar o Google Cloud SQL para o sistema de leads.

## Pré-requisitos

1. Conta no Google Cloud Platform
2. Projeto criado no GCP
3. Google Cloud CLI instalado (`gcloud`)
4. Permissões de administrador no projeto

## 1. Habilitar APIs necessárias

```bash
gcloud services enable sqladmin.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable vpcaccess.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
```

## 2. Criar instância Cloud SQL

### Opção A: Via Console (Recomendado para iniciantes)

1. Acesse [Google Cloud Console](https://console.cloud.google.com)
2. Navegue para SQL no menu lateral
3. Clique em "Criar Instância"
4. Escolha MySQL
5. Configure:
   - ID da instância: `sistema-leads-db`
   - Senha do root: (anote em local seguro)
   - Região: mesma do App Engine
   - Versão do MySQL: 8.0
   - Configuração da máquina: db-f1-micro (para começar)

### Opção B: Via CLI

```bash
# Definir variáveis
PROJECT_ID="seu-projeto-id"
INSTANCE_NAME="sistema-leads-db"
REGION="us-central1"
ROOT_PASSWORD="senha-super-segura"

# Criar instância
gcloud sql instances create $INSTANCE_NAME \
  --database-version=MYSQL_8_0 \
  --tier=db-f1-micro \
  --region=$REGION \
  --root-password=$ROOT_PASSWORD \
  --database-flags=character_set_server=utf8mb4,collation_server=utf8mb4_unicode_ci
```

## 3. Criar banco de dados

```bash
# Criar database
gcloud sql databases create sistema_db \
  --instance=$INSTANCE_NAME \
  --charset=utf8mb4 \
  --collation=utf8mb4_unicode_ci
```

## 4. Configurar conectividade

### Criar VPC Connector (necessário para App Engine)

```bash
# Criar VPC connector
gcloud compute networks vpc-access connectors create vpc-connector \
  --region=$REGION \
  --subnet-mode=auto \
  --max-instances=10 \
  --min-instances=2
```

### Configurar Cloud SQL Proxy (para desenvolvimento local)

1. Baixar Cloud SQL Proxy:
```bash
# Linux
wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
chmod +x cloud_sql_proxy

# macOS
curl -o cloud_sql_proxy https://dl.google.com/cloudsql/cloud_sql_proxy.darwin.amd64
chmod +x cloud_sql_proxy

# Windows
# Baixe de: https://dl.google.com/cloudsql/cloud_sql_proxy_x64.exe
```

2. Executar proxy:
```bash
./cloud_sql_proxy -instances=$PROJECT_ID:$REGION:$INSTANCE_NAME=tcp:3306
```

## 5. Criar tabelas

Conecte ao banco via proxy e execute:

```sql
USE sistema_db;

-- Tabela de usuários
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de chaves de produto
CREATE TABLE product_key (
    id INT AUTO_INCREMENT PRIMARY KEY,
    key_value VARCHAR(50) UNIQUE NOT NULL,
    total_leads INT NOT NULL,
    remaining_leads INT NOT NULL,
    user_id INT,
    activated_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

-- Tabela de configuração de banco
CREATE TABLE database_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    database_path VARCHAR(500) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de filtros salvos
CREATE TABLE saved_filter (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    filter_name VARCHAR(100) NOT NULL,
    filter_data TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

-- Índices para performance
CREATE INDEX idx_product_key_user ON product_key(user_id);
CREATE INDEX idx_saved_filter_user ON saved_filter(user_id);
```

## 6. Configurar variáveis de ambiente

No arquivo `.env`:

```env
# Cloud SQL
DB_USER=root
DB_PASS=sua-senha-root
DB_NAME=sistema_db
INSTANCE_CONNECTION_NAME=projeto-id:regiao:nome-instancia

# Para desenvolvimento local
DB_HOST=127.0.0.1
DB_PORT=3306
```

## 7. Configurar backup automático

```bash
# Configurar backup diário às 3h da manhã
gcloud sql instances patch $INSTANCE_NAME \
  --backup-start-time=03:00 \
  --backup-configuration
```

## 8. Monitoramento

### Métricas importantes:
- CPU utilization
- Memory usage
- Storage usage
- Connections count

### Configurar alertas:

1. No Console, vá para Monitoring
2. Crie políticas de alerta para:
   - CPU > 80%
   - Storage > 80%
   - Connections > 90% do limite

## Troubleshooting

### Erro de conexão no App Engine

Verifique:
1. VPC Connector está criado e configurado no app.yaml
2. INSTANCE_CONNECTION_NAME está correto
3. Service account tem permissões

### Erro de conexão local

Verifique:
1. Cloud SQL Proxy está rodando
2. Credenciais estão configuradas: `gcloud auth application-default login`
3. IP local está autorizado (se não usar proxy)

### Performance lenta

1. Verifique tier da instância (upgrade se necessário)
2. Analise queries lentas
3. Adicione índices apropriados
4. Configure connection pooling

## Custos estimados

- db-f1-micro: ~$15/mês
- Storage: $0.17/GB/mês
- Backup: $0.08/GB/mês
- Network: $0.12/GB (saída)

Total estimado para início: ~$20-30/mês

## Comandos úteis

```bash
# Ver detalhes da instância
gcloud sql instances describe $INSTANCE_NAME

# Listar bancos
gcloud sql databases list --instance=$INSTANCE_NAME

# Fazer backup manual
gcloud sql backups create --instance=$INSTANCE_NAME

# Ver logs
gcloud sql operations list --instance=$INSTANCE_NAME

# Conectar via CLI
gcloud sql connect $INSTANCE_NAME --user=root
```