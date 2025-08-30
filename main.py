# Este arquivo é usado apenas para deploy no App Engine
# Importa a aplicação do arquivo de produção

from app_production import app

if __name__ == '__main__':
    # O App Engine usa o Gunicorn para rodar a aplicação
    # Este bloco só é executado em desenvolvimento local
    app.run(host='0.0.0.0', port=8080, debug=False)