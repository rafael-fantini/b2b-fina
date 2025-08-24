from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import pandas as pd
import os
import secrets
import string
from datetime import datetime
import tempfile

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sistema.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)

# Modelos do banco de dados
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProductKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key_value = db.Column(db.String(50), unique=True, nullable=False)
    total_leads = db.Column(db.Integer, nullable=False)
    remaining_leads = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    activated_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DatabaseConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    database_path = db.Column(db.String(500), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class SavedFilter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filter_name = db.Column(db.String(100), nullable=False)
    filter_data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Funções utilitárias
def generate_product_key():
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16))

def get_current_database():
    config = DatabaseConfig.query.filter_by(is_active=True).first()
    if config:
        return config.database_path
    return 'data/empresas_teste.db'  # Banco padrão

def get_table_columns(db_path):
    """Retorna colunas de todas as tabelas com labels amigáveis"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Definir colunas disponíveis com labels amigáveis
        columns = {
            # Tabela empresas
            'e.cnpj_basico': 'CNPJ Básico',
            'e.razao_social': 'Razão Social',
            'e.natureza_juridica': 'Natureza Jurídica',
            'e.qualificacao_responsavel': 'Qualificação do Responsável',
            'e.porte_empresa': 'Porte da Empresa',
            
            # Tabela estabelecimento
            'est.cnpj_ordem': 'CNPJ Ordem',
            'est.cnpj_dv': 'CNPJ DV',
            'est.identificador_matriz_filial': 'Matriz/Filial',
            'est.nome_fantasia': 'Nome Fantasia',
            'est.situacao_cadastral': 'Situação Cadastral',
            'est.data_situacao_cadastral': 'Data Situação Cadastral',
            'est.data_inicio_atividade': 'Data Início Atividade',
            'est.cnae_fiscal_principal': 'CNAE Principal',
            'est.tipo_logradouro': 'Tipo Logradouro',
            'est.logradouro': 'Logradouro',
            'est.numero': 'Número',
            'est.complemento': 'Complemento',
            'est.bairro': 'Bairro',
            'est.cep': 'CEP',
            'est.uf': 'UF',
            'est.municipio': 'Município',
            'est.ddd_1': 'DDD 1',
            'est.telefone_1': 'Telefone 1',
            'est.ddd_2': 'DDD 2',
            'est.telefone_2': 'Telefone 2',
            'est.correio_eletronico': 'Email',
            
            # Tabela simples
            's.opcao_simples': 'Optante Simples',
            's.data_opcao_simples': 'Data Opção Simples',
            's.opcao_mei': 'Optante MEI',
            
            # Campos calculados
            'cnpj_completo': 'CNPJ Completo'
        }
        
        conn.close()
        return columns
    except Exception as e:
        print(f"Erro ao obter colunas: {e}")
        return {
            'e.cnpj_basico': 'CNPJ Básico',
            'e.razao_social': 'Razão Social',
            'est.nome_fantasia': 'Nome Fantasia',
            'est.uf': 'UF',
            's.opcao_simples': 'Optante Simples'
        }

def query_database(db_path, filters, selected_columns):
    try:
        conn = sqlite3.connect(db_path)
        
        # Construir query SQL com JOINs
        if selected_columns:
            # Adicionar CNPJ completo se selecionado
            select_parts = []
            for col in selected_columns:
                if col == 'cnpj_completo':
                    select_parts.append("(e.cnpj_basico || est.cnpj_ordem || est.cnpj_dv) as cnpj_completo")
                else:
                    select_parts.append(col)
            columns_str = ', '.join(select_parts)
        else:
            columns_str = 'e.cnpj_basico, e.razao_social, est.nome_fantasia, est.uf, s.opcao_simples'
        
        query = f"""
        SELECT {columns_str}
        FROM empresas e
        JOIN estabelecimento est ON e.cnpj_basico = est.cnpj_basico
        JOIN simples s ON e.cnpj_basico = s.cnpj_basico
        WHERE 1=1
        """
        
        params = []
        
        # Adicionar filtros
        for column, value in filters.items():
            if value and value.strip():
                if column == 'cnpj_completo':
                    query += " AND (e.cnpj_basico || est.cnpj_ordem || est.cnpj_dv) LIKE ?"
                else:
                    query += f" AND {column} LIKE ?"
                params.append(f"%{value.strip()}%")
        
        # Limitar resultados para não sobrecarregar
        query += " LIMIT 10000"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        print(f"Erro ao consultar banco: {e}")
        return pd.DataFrame()

# Rotas
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash('Login realizado com sucesso!', 'success')
            
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos!', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        product_key = request.form.get('product_key', '').strip()
        
        # Verificar se usuário já existe
        if User.query.filter_by(username=username).first():
            flash('Nome de usuário já existe!', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email já está em uso!', 'error')
            return render_template('register.html')
        
        # Verificar product key (apenas se foi fornecida)
        if product_key:
            key = ProductKey.query.filter_by(key_value=product_key, user_id=None).first()
            if not key:
                flash('Product Key inválida ou já utilizada!', 'error')
                return render_template('register.html')
        
        # Criar usuário
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        # Ativar product key se foi fornecida
        if product_key:
            key = ProductKey.query.filter_by(key_value=product_key, user_id=None).first()
            if key:
                key.user_id = user.id
                key.activated_at = datetime.utcnow()
                db.session.commit()
            flash('Cadastro realizado com sucesso! Product Key ativada.', 'success')
        else:
            flash('Cadastro realizado com sucesso! Adicione uma Product Key no dashboard para acessar as funcionalidades.', 'info')
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('is_admin'):
        flash('Acesso negado!', 'error')
        return redirect(url_for('index'))
    
    users = User.query.all()
    product_keys = ProductKey.query.all()
    database_config = DatabaseConfig.query.filter_by(is_active=True).first()
    
    return render_template('admin.html', 
                         users=users, 
                         product_keys=product_keys,
                         database_config=database_config)

@app.route('/admin/generate-keys', methods=['POST'])
def generate_keys():
    if not session.get('is_admin'):
        return jsonify({'error': 'Acesso negado'}), 403
    
    lead_count = int(request.form['lead_count'])
    quantity = int(request.form['quantity'])
    
    keys = []
    for _ in range(quantity):
        key = ProductKey(
            key_value=generate_product_key(),
            total_leads=lead_count,
            remaining_leads=lead_count
        )
        db.session.add(key)
        keys.append(key.key_value)
    
    db.session.commit()
    
    return jsonify({'success': True, 'keys': keys})

@app.route('/filter')
def filter_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Verificar se usuário tem Product Key ativa
    user_id = session['user_id']
    product_key = ProductKey.query.filter_by(user_id=user_id).first()
    
    if not product_key:
        flash('Para acessar os filtros, você precisa de uma Product Key ativa. Adicione uma no dashboard.', 'warning')
        return redirect(url_for('index'))
    
    if product_key.remaining_leads <= 0:
        flash('Seus leads acabaram! Adicione uma nova Product Key para continuar.', 'warning')
        return redirect(url_for('index'))
    
    db_path = get_current_database()
    columns = get_table_columns(db_path)
    
    # Buscar filtros salvos do usuário
    saved_filters = SavedFilter.query.filter_by(user_id=session['user_id']).all()
    
    return render_template('filter.html', columns=columns, saved_filters=saved_filters)

@app.route('/export', methods=['POST'])
def export_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    # Verificar leads disponíveis
    user_id = session['user_id']
    product_key = ProductKey.query.filter_by(user_id=user_id).first()
    
    if not product_key or product_key.remaining_leads <= 0:
        return jsonify({'error': 'Leads insuficientes'}), 400
    
    data = request.get_json()
    filters = data.get('filters', {})
    selected_columns = data.get('columns', [])
    export_format = data.get('format', 'csv')
    
    db_path = get_current_database()
    df = query_database(db_path, filters, selected_columns)
    
    if df.empty:
        return jsonify({'error': 'Nenhum resultado encontrado'}), 400
    
    # Reduzir leads disponíveis
    leads_used = min(len(df), product_key.remaining_leads)
    product_key.remaining_leads -= leads_used
    db.session.commit()
    
    # Criar arquivo temporário
    temp_dir = tempfile.mkdtemp()
    
    if export_format == 'xlsx':
        filename = f'dados_exportados_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        filepath = os.path.join(temp_dir, filename)
        df.head(leads_used).to_excel(filepath, index=False)
    else:
        filename = f'dados_exportados_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        filepath = os.path.join(temp_dir, filename)
        df.head(leads_used).to_csv(filepath, index=False)
    
    return send_file(filepath, as_attachment=True, download_name=filename)

@app.route('/save-filter', methods=['POST'])
def save_filter():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.get_json()
    filter_name = data.get('name')
    filter_data = data.get('filters')
    
    saved_filter = SavedFilter(
        user_id=session['user_id'],
        filter_name=filter_name,
        filter_data=str(filter_data)
    )
    
    db.session.add(saved_filter)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/admin/upload-database', methods=['POST'])
def upload_database():
    if not session.get('is_admin'):
        return jsonify({'error': 'Acesso negado'}), 403
    
    if 'database' not in request.files:
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    file = request.files['database']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    if file and file.filename.endswith('.db'):
        # Criar diretório se não existir
        os.makedirs('uploads', exist_ok=True)
        
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads', filename)
        file.save(filepath)
        
        # Desativar banco anterior
        DatabaseConfig.query.update({'is_active': False})
        
        # Adicionar novo banco
        new_db = DatabaseConfig(database_path=filepath)
        db.session.add(new_db)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Banco de dados atualizado com sucesso!'})
    
    return jsonify({'error': 'Formato de arquivo inválido'}), 400

# APIs para o dashboard e sistema de filtros

@app.route('/api/dashboard-stats')
def dashboard_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    user_id = session['user_id']
    
    # Buscar informações do usuário
    product_key = ProductKey.query.filter_by(user_id=user_id).first()
    
    # Estatísticas básicas
    stats = {
        'leads_remaining': product_key.remaining_leads if product_key else 0,
        'total_leads': product_key.total_leads if product_key else 0,
        'exports_today': 0,  # Implementar contagem de exportações
        'saved_filters': SavedFilter.query.filter_by(user_id=user_id).count(),
        'total_companies': 0
    }
    
    # Definir tipo de plano
    if product_key:
        if product_key.total_leads >= 50000:
            stats['plan_type'] = 'Premium'
        elif product_key.total_leads >= 10000:
            stats['plan_type'] = 'Professional'
        elif product_key.total_leads >= 2000:
            stats['plan_type'] = 'Standard'
        else:
            stats['plan_type'] = 'Básico'
    
    # Buscar estatísticas do banco
    try:
        db_path = get_current_database()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Total de empresas
        cursor.execute("SELECT COUNT(*) FROM empresas")
        stats['total_companies'] = cursor.fetchone()[0]
        
        # Distribuição por estado
        cursor.execute("""
            SELECT est.uf, COUNT(*) as count
            FROM empresas e
            JOIN estabelecimento est ON e.cnpj_basico = est.cnpj_basico
            GROUP BY est.uf
            ORDER BY count DESC
            LIMIT 10
        """)
        stats['state_distribution'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Distribuição do Simples Nacional
        cursor.execute("""
            SELECT s.opcao_simples, COUNT(*) as count
            FROM simples s
            GROUP BY s.opcao_simples
        """)
        simples_data = cursor.fetchall()
        stats['simples_distribution'] = {
            'optante': next((row[1] for row in simples_data if row[0] == 'S'), 0),
            'nao_optante': next((row[1] for row in simples_data if row[0] == 'N'), 0)
        }
        
        conn.close()
    except Exception as e:
        print(f"Erro ao buscar estatísticas: {e}")
    
    return jsonify(stats)

@app.route('/api/preview', methods=['POST'])
def preview_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    # Verificar se usuário tem Product Key ativa
    user_id = session['user_id']
    product_key = ProductKey.query.filter_by(user_id=user_id).first()
    
    if not product_key:
        return jsonify({'error': 'Product Key necessária para fazer pesquisas'}), 403
    
    if product_key.remaining_leads <= 0:
        return jsonify({'error': 'Leads insuficientes. Adicione uma nova Product Key.'}), 403
    
    data = request.get_json()
    filters = data.get('filters', {})
    selected_columns = data.get('columns', [])
    
    db_path = get_current_database()
    df = query_database(db_path, filters, selected_columns)
    
    # Limitar preview a 50 registros
    preview_df = df.head(50)
    
    return jsonify({
        'results': preview_df.to_dict('records'),
        'count': len(df),
        'preview_count': len(preview_df)
    })

@app.route('/api/user-leads')
def user_leads():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    user_id = session['user_id']
    product_key = ProductKey.query.filter_by(user_id=user_id).first()
    
    return jsonify({
        'remaining_leads': product_key.remaining_leads if product_key else 0,
        'total_leads': product_key.total_leads if product_key else 0
    })

@app.route('/api/quick-export', methods=['POST'])
def quick_export():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    # Verificar leads disponíveis
    user_id = session['user_id']
    product_key = ProductKey.query.filter_by(user_id=user_id).first()
    
    if not product_key or product_key.remaining_leads <= 0:
        return jsonify({'error': 'Leads insuficientes'}), 400
    
    data = request.get_json()
    export_format = data.get('format', 'csv')
    
    # Filtro pré-definido para empresas ativas
    filters = {'est.situacao_cadastral': '02'}  # 02 = ATIVA
    
    # Colunas padrão para export rápido
    selected_columns = [
        'e.cnpj_basico', 'e.razao_social', 'est.nome_fantasia', 
        'est.uf', 'est.telefone_1', 'est.correio_eletronico', 
        's.opcao_simples'
    ]
    
    db_path = get_current_database()
    df = query_database(db_path, filters, selected_columns)
    
    if df.empty:
        return jsonify({'error': 'Nenhum resultado encontrado'}), 400
    
    # Reduzir leads disponíveis
    leads_used = min(len(df), product_key.remaining_leads)
    product_key.remaining_leads -= leads_used
    db.session.commit()
    
    # Criar arquivo temporário
    temp_dir = tempfile.mkdtemp()
    
    if export_format == 'xlsx':
        filename = f'empresas_ativas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        filepath = os.path.join(temp_dir, filename)
        df.head(leads_used).to_excel(filepath, index=False)
    else:
        filename = f'empresas_ativas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        filepath = os.path.join(temp_dir, filename)
        df.head(leads_used).to_csv(filepath, index=False)
    
    return send_file(filepath, as_attachment=True, download_name=filename)

@app.route('/admin/reset-leads', methods=['POST'])
def reset_leads():
    if not session.get('is_admin'):
        return jsonify({'error': 'Acesso negado'}), 403
    
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'ID do usuário não fornecido'}), 400
    
    # Buscar product key do usuário
    product_key = ProductKey.query.filter_by(user_id=user_id).first()
    
    if not product_key:
        return jsonify({'error': 'Usuário não possui product key'}), 400
    
    # Resetar leads
    product_key.remaining_leads = product_key.total_leads
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Leads resetados com sucesso!'})

@app.route('/add-product-key', methods=['POST'])
def add_product_key():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.get_json()
    product_key_value = data.get('product_key', '').strip().upper()
    
    if not product_key_value:
        return jsonify({'error': 'Product Key não fornecida'}), 400
    
    user_id = session['user_id']
    
    # Verificar se a key existe e está disponível
    new_key = ProductKey.query.filter_by(key_value=product_key_value, user_id=None).first()
    
    if not new_key:
        return jsonify({'error': 'Product Key inválida ou já utilizada'}), 400
    
    # Verificar se o usuário já tem uma key ativa
    existing_key = ProductKey.query.filter_by(user_id=user_id).first()
    
    if existing_key:
        # Somar os leads da nova key à key existente
        existing_key.remaining_leads += new_key.total_leads
        existing_key.total_leads += new_key.total_leads
        
        # Marcar a nova key como usada pelo mesmo usuário
        new_key.user_id = user_id
        new_key.activated_at = datetime.utcnow()
        new_key.remaining_leads = 0  # Transferidos para a key principal
    else:
        # Primeira key do usuário
        new_key.user_id = user_id
        new_key.activated_at = datetime.utcnow()
    
    db.session.commit()
    
    # Calcular total de leads atual
    current_key = ProductKey.query.filter_by(user_id=user_id).first()
    total_leads = current_key.remaining_leads if current_key else 0
    
    return jsonify({
        'success': True, 
        'message': f'Product Key ativada! {new_key.total_leads} leads adicionados.',
        'total_leads': total_leads
    })

if __name__ == '__main__':
    # Criar diretórios necessários
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    with app.app_context():
        db.create_all()
        
        # Criar usuário admin se não existir
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                email='admin@sistema.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
        
        # Criar algumas Product Keys de teste se não existirem
        if ProductKey.query.count() == 0:
            test_keys = [
                {'leads': 1000, 'count': 2},
                {'leads': 2000, 'count': 2},
                {'leads': 10000, 'count': 1},
                {'leads': 50000, 'count': 1}
            ]
            
            for key_config in test_keys:
                for _ in range(key_config['count']):
                    test_key = ProductKey(
                        key_value=generate_product_key(),
                        total_leads=key_config['leads'],
                        remaining_leads=key_config['leads']
                    )
                    db.session.add(test_key)
            
            db.session.commit()
            print("Product Keys de teste criadas automaticamente!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
