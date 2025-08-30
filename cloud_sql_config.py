"""
Configuração para Google Cloud SQL
"""
import os
import sqlalchemy

# Configurações do Cloud SQL
def get_cloud_sql_connection():
    """Retorna uma conexão com o Cloud SQL"""
    
    # Configurações de conexão
    db_user = os.environ.get("DB_USER", "root")
    db_pass = os.environ.get("DB_PASS", "")
    db_name = os.environ.get("DB_NAME", "sistema_db")
    db_socket_dir = os.environ.get("DB_SOCKET_DIR", "/cloudsql")
    instance_connection_name = os.environ.get("INSTANCE_CONNECTION_NAME", "")
    
    # Se estiver rodando no App Engine
    if os.environ.get('GAE_ENV', '').startswith('standard'):
        # Usa Unix socket
        db_socket = f"{db_socket_dir}/{instance_connection_name}"
        
        pool = sqlalchemy.create_engine(
            sqlalchemy.engine.url.URL.create(
                drivername="mysql+pymysql",
                username=db_user,
                password=db_pass,
                database=db_name,
                query={"unix_socket": db_socket}
            ),
            pool_size=5,
            max_overflow=2,
            pool_timeout=30,
            pool_recycle=1800,
        )
    else:
        # Desenvolvimento local - usa IP público
        db_host = os.environ.get("DB_HOST", "127.0.0.1")
        db_port = os.environ.get("DB_PORT", "3306")
        
        pool = sqlalchemy.create_engine(
            sqlalchemy.engine.url.URL.create(
                drivername="mysql+pymysql",
                username=db_user,
                password=db_pass,
                host=db_host,
                port=db_port,
                database=db_name
            ),
            pool_size=5,
            max_overflow=2,
            pool_timeout=30,
            pool_recycle=1800,
        )
    
    return pool

def get_database_uri():
    """Retorna a URI do banco de dados para SQLAlchemy"""
    
    db_user = os.environ.get("DB_USER", "root")
    db_pass = os.environ.get("DB_PASS", "")
    db_name = os.environ.get("DB_NAME", "sistema_db")
    
    # Se estiver rodando no App Engine
    if os.environ.get('GAE_ENV', '').startswith('standard'):
        db_socket_dir = os.environ.get("DB_SOCKET_DIR", "/cloudsql")
        instance_connection_name = os.environ.get("INSTANCE_CONNECTION_NAME", "")
        
        return f"mysql+pymysql://{db_user}:{db_pass}@/{db_name}?unix_socket={db_socket_dir}/{instance_connection_name}"
    else:
        # Desenvolvimento local
        db_host = os.environ.get("DB_HOST", "127.0.0.1")
        db_port = os.environ.get("DB_PORT", "3306")
        
        return f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"