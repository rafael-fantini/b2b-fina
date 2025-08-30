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
from cloud_sql_config import get_database_uri

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sua-chave-secreta-aqui')

# Configuração do banco de dados
if os.environ.get('GAE_ENV', '').startswith('standard'):
    # Produção - usa Cloud SQL
    app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
else:
    # Desenvolvimento - usa SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sistema.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')

# Garante que a pasta de upload existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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

# Criar as tabelas se não existirem
with app.app_context():
    db.create_all()

# Função para gerar chave de produto
def generate_product_key():
    """Gera uma chave de produto única"""
    characters = string.ascii_uppercase + string.digits
    while True:
        key = ''.join(secrets.choice(characters) for _ in range(16))
        formatted_key = f"{key[:4]}-{key[4:8]}-{key[8:12]}-{key[12:16]}"
        if not ProductKey.query.filter_by(key_value=formatted_key).first():
            return formatted_key

# Decorador para verificar se o usuário está logado
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para verificar se o usuário é admin
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Você não tem permissão para acessar esta página.', 'danger')
            return redirect(url_for('home'))
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Verificar se o usuário já existe
        if User.query.filter_by(username=username).first():
            flash('Nome de usuário já existe!', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('E-mail já cadastrado!', 'danger')
            return redirect(url_for('register'))
        
        # Criar novo usuário
        password_hash = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            is_admin=False
        )
        
        # O primeiro usuário é sempre admin
        if User.query.count() == 0:
            new_user.is_admin = True
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Usuário ou senha incorretos!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/home')
@login_required
def home():
    user_id = session.get('user_id')
    
    # Buscar chave do usuário
    product_key = ProductKey.query.filter_by(user_id=user_id).first()
    
    # Buscar filtros salvos do usuário
    saved_filters = SavedFilter.query.filter_by(user_id=user_id).all()
    
    return render_template('home.html', product_key=product_key, saved_filters=saved_filters)

@app.route('/activate_key', methods=['POST'])
@login_required
def activate_key():
    key_value = request.form.get('product_key')
    user_id = session.get('user_id')
    
    # Verificar se o usuário já tem uma chave ativa
    existing_key = ProductKey.query.filter_by(user_id=user_id).first()
    if existing_key:
        flash('Você já possui uma chave ativa!', 'warning')
        return redirect(url_for('home'))
    
    # Buscar a chave
    product_key = ProductKey.query.filter_by(key_value=key_value).first()
    
    if not product_key:
        flash('Chave de produto inválida!', 'danger')
        return redirect(url_for('home'))
    
    if product_key.user_id is not None:
        flash('Esta chave já foi ativada!', 'danger')
        return redirect(url_for('home'))
    
    # Ativar a chave
    product_key.user_id = user_id
    product_key.activated_at = datetime.utcnow()
    db.session.commit()
    
    flash('Chave ativada com sucesso!', 'success')
    return redirect(url_for('home'))

@app.route('/search_leads')
@login_required
def search_leads():
    user_id = session.get('user_id')
    
    # Verificar se o usuário tem uma chave ativa com leads disponíveis
    product_key = ProductKey.query.filter_by(user_id=user_id).first()
    
    if not product_key:
        flash('Você precisa ativar uma chave de produto primeiro!', 'warning')
        return redirect(url_for('home'))
    
    if product_key.remaining_leads <= 0:
        flash('Você não possui leads disponíveis!', 'danger')
        return redirect(url_for('home'))
    
    # Buscar banco de dados ativo
    db_config = DatabaseConfig.query.filter_by(is_active=True).first()
    
    if not db_config:
        flash('Nenhum banco de dados configurado. Entre em contato com o administrador.', 'danger')
        return redirect(url_for('home'))
    
    return render_template('search_leads.html', remaining_leads=product_key.remaining_leads)

@app.route('/api/search', methods=['POST'])
@login_required
def api_search():
    user_id = session.get('user_id')
    data = request.get_json()
    
    # Verificar se o usuário tem leads disponíveis
    product_key = ProductKey.query.filter_by(user_id=user_id).first()
    
    if not product_key or product_key.remaining_leads <= 0:
        return jsonify({'error': 'Sem leads disponíveis'}), 403
    
    # Buscar banco de dados ativo
    db_config = DatabaseConfig.query.filter_by(is_active=True).first()
    
    if not db_config:
        return jsonify({'error': 'Nenhum banco de dados configurado'}), 500
    
    try:
        # Conectar ao banco de dados SQLite
        conn = sqlite3.connect(db_config.database_path)
        
        # Construir query baseada nos filtros
        query = "SELECT * FROM leads WHERE 1=1"
        params = []
        
        # Adicionar filtros
        filters = data.get('filters', {})
        
        if filters.get('nome'):
            query += " AND nome LIKE ?"
            params.append(f"%{filters['nome']}%")
        
        if filters.get('email'):
            query += " AND email LIKE ?"
            params.append(f"%{filters['email']}%")
        
        if filters.get('telefone'):
            query += " AND telefone LIKE ?"
            params.append(f"%{filters['telefone']}%")
        
        if filters.get('cidade'):
            query += " AND cidade LIKE ?"
            params.append(f"%{filters['cidade']}%")
        
        if filters.get('estado'):
            query += " AND estado = ?"
            params.append(filters['estado'])
        
        if filters.get('idade_min'):
            query += " AND idade >= ?"
            params.append(int(filters['idade_min']))
        
        if filters.get('idade_max'):
            query += " AND idade <= ?"
            params.append(int(filters['idade_max']))
        
        if filters.get('genero'):
            query += " AND genero = ?"
            params.append(filters['genero'])
        
        # Limitar resultados
        limit = min(int(data.get('limit', 10)), product_key.remaining_leads, 100)
        query += f" LIMIT {limit}"
        
        # Executar query
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        # Converter para JSON
        results = df.to_dict('records')
        
        # Atualizar leads restantes
        leads_used = len(results)
        product_key.remaining_leads -= leads_used
        db.session.commit()
        
        return jsonify({
            'results': results,
            'count': len(results),
            'remaining_leads': product_key.remaining_leads
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save_filter', methods=['POST'])
@login_required
def save_filter():
    user_id = session.get('user_id')
    data = request.get_json()
    
    filter_name = data.get('name')
    filter_data = data.get('filters')
    
    if not filter_name or not filter_data:
        return jsonify({'error': 'Dados inválidos'}), 400
    
    # Criar novo filtro salvo
    saved_filter = SavedFilter(
        user_id=user_id,
        filter_name=filter_name,
        filter_data=str(filter_data)
    )
    
    db.session.add(saved_filter)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Filtro salvo com sucesso!'})

@app.route('/delete_filter/<int:filter_id>', methods=['POST'])
@login_required
def delete_filter(filter_id):
    user_id = session.get('user_id')
    
    saved_filter = SavedFilter.query.filter_by(id=filter_id, user_id=user_id).first()
    
    if saved_filter:
        db.session.delete(saved_filter)
        db.session.commit()
        flash('Filtro excluído com sucesso!', 'success')
    else:
        flash('Filtro não encontrado!', 'danger')
    
    return redirect(url_for('home'))

@app.route('/export_results', methods=['POST'])
@login_required
def export_results():
    data = request.get_json()
    results = data.get('results', [])
    
    if not results:
        return jsonify({'error': 'Nenhum resultado para exportar'}), 400
    
    # Criar DataFrame
    df = pd.DataFrame(results)
    
    # Criar arquivo Excel temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        df.to_excel(tmp.name, index=False)
        tmp_path = tmp.name
    
    # Enviar arquivo
    response = send_file(
        tmp_path,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'leads_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )
    
    # Remover arquivo temporário após envio
    @response.call_on_close
    def remove_file(response):
        try:
            os.remove(tmp_path)
        except:
            pass
    
    return response

# Rotas administrativas
@app.route('/admin')
@admin_required
def admin_dashboard():
    # Estatísticas
    total_users = User.query.count()
    total_keys = ProductKey.query.count()
    active_keys = ProductKey.query.filter(ProductKey.user_id.isnot(None)).count()
    
    # Listar usuários recentes
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    # Listar chaves recentes
    recent_keys = ProductKey.query.order_by(ProductKey.created_at.desc()).limit(10).all()
    
    # Configuração do banco de dados
    db_config = DatabaseConfig.query.filter_by(is_active=True).first()
    
    return render_template('admin_dashboard.html',
                         total_users=total_users,
                         total_keys=total_keys,
                         active_keys=active_keys,
                         recent_users=recent_users,
                         recent_keys=recent_keys,
                         db_config=db_config)

@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/toggle_admin/<int:user_id>', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    user = User.query.get(user_id)
    
    if not user:
        flash('Usuário não encontrado!', 'danger')
        return redirect(url_for('admin_users'))
    
    # Não permitir remover admin do próprio usuário
    if user.id == session.get('user_id'):
        flash('Você não pode remover suas próprias permissões de admin!', 'danger')
        return redirect(url_for('admin_users'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    flash(f'Permissões de {user.username} atualizadas com sucesso!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    
    if not user:
        flash('Usuário não encontrado!', 'danger')
        return redirect(url_for('admin_users'))
    
    # Não permitir deletar o próprio usuário
    if user.id == session.get('user_id'):
        flash('Você não pode deletar sua própria conta!', 'danger')
        return redirect(url_for('admin_users'))
    
    # Liberar chave do usuário se houver
    product_key = ProductKey.query.filter_by(user_id=user_id).first()
    if product_key:
        product_key.user_id = None
        product_key.activated_at = None
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Usuário {user.username} deletado com sucesso!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/keys')
@admin_required
def admin_keys():
    keys = ProductKey.query.order_by(ProductKey.created_at.desc()).all()
    return render_template('admin_keys.html', keys=keys)

@app.route('/admin/generate_keys', methods=['POST'])
@admin_required
def generate_keys():
    quantity = int(request.form.get('quantity', 1))
    leads_per_key = int(request.form.get('leads_per_key', 100))
    
    keys_generated = []
    
    for _ in range(quantity):
        key_value = generate_product_key()
        new_key = ProductKey(
            key_value=key_value,
            total_leads=leads_per_key,
            remaining_leads=leads_per_key
        )
        db.session.add(new_key)
        keys_generated.append(key_value)
    
    db.session.commit()
    
    flash(f'{quantity} chave(s) gerada(s) com sucesso!', 'success')
    
    # Retornar as chaves geradas para exibição
    return render_template('generated_keys.html', keys=keys_generated)

@app.route('/admin/delete_key/<int:key_id>', methods=['POST'])
@admin_required
def delete_key(key_id):
    key = ProductKey.query.get(key_id)
    
    if not key:
        flash('Chave não encontrada!', 'danger')
        return redirect(url_for('admin_keys'))
    
    db.session.delete(key)
    db.session.commit()
    
    flash('Chave deletada com sucesso!', 'success')
    return redirect(url_for('admin_keys'))

@app.route('/admin/database')
@admin_required
def admin_database():
    db_configs = DatabaseConfig.query.order_by(DatabaseConfig.uploaded_at.desc()).all()
    return render_template('admin_database.html', db_configs=db_configs)

@app.route('/admin/upload_database', methods=['POST'])
@admin_required
def upload_database():
    if 'database' not in request.files:
        flash('Nenhum arquivo selecionado!', 'danger')
        return redirect(url_for('admin_database'))
    
    file = request.files['database']
    
    if file.filename == '':
        flash('Nenhum arquivo selecionado!', 'danger')
        return redirect(url_for('admin_database'))
    
    if file and file.filename.endswith('.db'):
        # Salvar arquivo
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"leads_{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Verificar se o arquivo é um banco SQLite válido
        try:
            conn = sqlite3.connect(filepath)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='leads'")
            if not cursor.fetchone():
                conn.close()
                os.remove(filepath)
                flash('Banco de dados inválido! A tabela "leads" não foi encontrada.', 'danger')
                return redirect(url_for('admin_database'))
            conn.close()
        except Exception as e:
            os.remove(filepath)
            flash(f'Erro ao verificar banco de dados: {str(e)}', 'danger')
            return redirect(url_for('admin_database'))
        
        # Desativar outros bancos
        DatabaseConfig.query.update({DatabaseConfig.is_active: False})
        
        # Criar nova configuração
        new_config = DatabaseConfig(
            database_path=filepath,
            is_active=True
        )
        db.session.add(new_config)
        db.session.commit()
        
        flash('Banco de dados carregado com sucesso!', 'success')
    else:
        flash('Por favor, envie um arquivo .db válido!', 'danger')
    
    return redirect(url_for('admin_database'))

@app.route('/admin/activate_database/<int:db_id>', methods=['POST'])
@admin_required
def activate_database(db_id):
    # Desativar todos os bancos
    DatabaseConfig.query.update({DatabaseConfig.is_active: False})
    
    # Ativar o banco selecionado
    db_config = DatabaseConfig.query.get(db_id)
    if db_config:
        db_config.is_active = True
        db.session.commit()
        flash('Banco de dados ativado com sucesso!', 'success')
    else:
        flash('Banco de dados não encontrado!', 'danger')
    
    return redirect(url_for('admin_database'))

@app.route('/admin/delete_database/<int:db_id>', methods=['POST'])
@admin_required
def delete_database(db_id):
    db_config = DatabaseConfig.query.get(db_id)
    
    if not db_config:
        flash('Banco de dados não encontrado!', 'danger')
        return redirect(url_for('admin_database'))
    
    # Remover arquivo
    try:
        os.remove(db_config.database_path)
    except:
        pass
    
    # Remover do banco
    db.session.delete(db_config)
    db.session.commit()
    
    flash('Banco de dados removido com sucesso!', 'success')
    return redirect(url_for('admin_database'))

if __name__ == '__main__':
    # Em produção, o App Engine usa o Gunicorn
    # Em desenvolvimento, usa o servidor de desenvolvimento do Flask
    if os.environ.get('GAE_ENV', '').startswith('standard'):
        # Produção
        app.run()
    else:
        # Desenvolvimento
        app.run(debug=True, host='0.0.0.0', port=5000)