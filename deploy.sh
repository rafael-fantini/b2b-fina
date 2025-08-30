#!/bin/bash

# Script de deploy para Google Cloud e Firebase
# Certifique-se de ter gcloud CLI e firebase-tools instalados

echo "=== Deploy Script para Google Cloud e Firebase ==="
echo ""

# Verificar se as ferramentas estão instaladas
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI não encontrado. Por favor, instale: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

if ! command -v firebase &> /dev/null; then
    echo "❌ firebase-tools não encontrado. Por favor, instale: npm install -g firebase-tools"
    exit 1
fi

# Solicitar informações do projeto
read -p "Digite o ID do seu projeto Google Cloud: " PROJECT_ID
read -p "Digite a região (ex: us-central1): " REGION
read -p "Digite o nome da instância Cloud SQL: " INSTANCE_NAME

# Configurar projeto
echo ""
echo "📋 Configurando projeto..."
gcloud config set project $PROJECT_ID

# Criar app.yaml com as configurações corretas
echo ""
echo "📝 Atualizando app.yaml..."
sed -i "s/YOUR_PROJECT_ID/$PROJECT_ID/g" app.yaml
sed -i "s/YOUR_REGION/$REGION/g" app.yaml
sed -i "s/YOUR_CONNECTOR_NAME/vpc-connector/g" app.yaml

# Atualizar .firebaserc
echo ""
echo "📝 Atualizando .firebaserc..."
sed -i "s/your-project-id/$PROJECT_ID/g" .firebaserc

# Criar arquivo de variáveis de ambiente
echo ""
echo "📝 Criando arquivo .env para deploy..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Por favor, edite o arquivo .env com suas configurações antes de continuar."
    echo "   Especialmente:"
    echo "   - SECRET_KEY"
    echo "   - DB_USER e DB_PASS"
    echo "   - INSTANCE_CONNECTION_NAME ($PROJECT_ID:$REGION:$INSTANCE_NAME)"
    read -p "Pressione ENTER quando terminar de editar o .env..."
fi

# Deploy do App Engine
echo ""
echo "🚀 Fazendo deploy no App Engine..."
echo "   Usando app_production.py como main.py..."
cp app_production.py main.py

# Criar arquivo de configuração do App Engine
cat > app.yaml << EOF
runtime: python311

instance_class: F2

env_variables:
  FLASK_ENV: "production"
  INSTANCE_CONNECTION_NAME: "$PROJECT_ID:$REGION:$INSTANCE_NAME"
  DB_SOCKET_DIR: "/cloudsql"

automatic_scaling:
  target_cpu_utilization: 0.65
  min_instances: 1
  max_instances: 10
  min_pending_latency: 30ms
  max_pending_latency: automatic
  max_concurrent_requests: 50

handlers:
- url: /static
  static_dir: static
  secure: always
  http_headers:
    Cache-Control: "public, max-age=31536000"

- url: /.*
  script: auto
  secure: always

vpc_access_connector:
  name: projects/$PROJECT_ID/locations/$REGION/connectors/vpc-connector

entrypoint: gunicorn -b :8080 main:app
EOF

# Deploy
gcloud app deploy --quiet

# Limpar
rm -f main.py

# Deploy das regras do Firebase (se necessário)
echo ""
echo "🔥 Configurando Firebase..."
firebase use $PROJECT_ID

echo ""
echo "✅ Deploy concluído!"
echo ""
echo "📌 Próximos passos:"
echo "1. Certifique-se de que o Cloud SQL está configurado e acessível"
echo "2. Configure as variáveis de ambiente no App Engine Console"
echo "3. Teste sua aplicação em: https://$PROJECT_ID.appspot.com"
echo ""
echo "📚 Comandos úteis:"
echo "   Ver logs: gcloud app logs tail -s default"
echo "   Ver versões: gcloud app versions list"
echo "   Configurar domínio: gcloud app domain-mappings create SEU_DOMINIO"