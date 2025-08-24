import sqlite3
import random
from faker import Faker
from faker.providers import company
import pandas as pd
import os

# Configurar Faker para português brasileiro
fake = Faker('pt_BR')
fake.add_provider(company)

def generate_cnpj():
    """Gera um CNPJ válido"""
    def calculate_digit(cnpj, weights):
        sum_result = sum(int(cnpj[i]) * weights[i] for i in range(len(weights)))
        remainder = sum_result % 11
        return 0 if remainder < 2 else 11 - remainder
    
    # Gerar os primeiros 12 dígitos
    cnpj = [random.randint(0, 9) for _ in range(12)]
    
    # Calcular primeiro dígito verificador
    weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    cnpj.append(calculate_digit(cnpj, weights1))
    
    # Calcular segundo dígito verificador
    weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    cnpj.append(calculate_digit(cnpj, weights2))
    
    return ''.join(map(str, cnpj))

def generate_cnpj_basico():
    """Gera apenas os 8 primeiros dígitos do CNPJ"""
    return str(random.randint(10000000, 99999999))

def format_cnpj(cnpj_basico, ordem="0001", dv="00"):
    """Formata CNPJ completo"""
    cnpj_full = cnpj_basico + ordem + dv
    return f"{cnpj_full[:2]}.{cnpj_full[2:5]}.{cnpj_full[5:8]}/{cnpj_full[8:12]}-{cnpj_full[12:14]}"

def generate_phone():
    """Gera um telefone brasileiro"""
    ddd = random.choice(['11', '21', '31', '41', '47', '48', '51', '61', '62', '71', '81', '85'])
    if random.choice([True, False]):
        # Celular
        return f"({ddd}) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    else:
        # Fixo
        return f"({ddd}) {random.randint(3000, 5999)}-{random.randint(1000, 9999)}"

def generate_email(company_name):
    """Gera email baseado no nome da empresa"""
    clean_name = company_name.lower().replace(' ', '').replace('.', '').replace(',', '')[:10]
    return f"contato@{clean_name}.{random.choice(['com.br', 'net.br', 'org.br'])}"

def create_test_database():
    """Cria banco de dados de teste com empresas brasileiras seguindo a estrutura real"""
    
    # Criar diretório se não existir
    os.makedirs('data', exist_ok=True)
    
    # Conectar ao banco
    conn = sqlite3.connect('data/empresas_teste.db')
    cursor = conn.cursor()
    
    # Criar tabelas de referência primeiro
    
    # Tabela natureza_juridica
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS natureza_juridica (
        codigo TEXT PRIMARY KEY,
        descricao TEXT
    )
    ''')
    
    # Tabela qualificacao_socio
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS qualificacao_socio (
        codigo TEXT PRIMARY KEY,
        descricao TEXT
    )
    ''')
    
    # Tabela pais
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pais (
        codigo TEXT PRIMARY KEY,
        descricao TEXT
    )
    ''')
    
    # Tabela municipio
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS municipio (
        codigo TEXT PRIMARY KEY,
        descricao TEXT
    )
    ''')
    
    # Tabela motivo
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS motivo (
        codigo TEXT PRIMARY KEY,
        descricao TEXT
    )
    ''')
    
    # Tabela cnae
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cnae (
        codigo TEXT PRIMARY KEY,
        descricao TEXT
    )
    ''')
    
    # Tabela empresas (principal)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS empresas (
        cnpj_basico TEXT PRIMARY KEY,
        razao_social TEXT,
        natureza_juridica TEXT,
        qualificacao_responsavel TEXT,
        capital_social TEXT,
        porte_empresa TEXT,
        ente_federativo_responsavel TEXT
    )
    ''')
    
    # Tabela estabelecimento
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS estabelecimento (
        cnpj_basico TEXT,
        cnpj_ordem TEXT,
        cnpj_dv TEXT,
        identificador_matriz_filial TEXT,
        nome_fantasia TEXT,
        situacao_cadastral TEXT,
        data_situacao_cadastral TEXT,
        motivo_situacao_cadastral TEXT,
        nome_cidade_exterior TEXT,
        pais TEXT,
        data_inicio_atividade TEXT,
        cnae_fiscal_principal TEXT,
        cnae_fiscal_secundaria TEXT,
        tipo_logradouro TEXT,
        logradouro TEXT,
        numero TEXT,
        complemento TEXT,
        bairro TEXT,
        cep TEXT,
        uf TEXT,
        municipio TEXT,
        ddd_1 TEXT,
        telefone_1 TEXT,
        ddd_2 TEXT,
        telefone_2 TEXT,
        ddd_fax TEXT,
        fax TEXT,
        correio_eletronico TEXT,
        situacao_especial TEXT,
        data_situacao_especial TEXT,
        PRIMARY KEY (cnpj_basico, cnpj_ordem, cnpj_dv)
    )
    ''')
    
    # Tabela simples
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS simples (
        cnpj_basico TEXT PRIMARY KEY,
        opcao_simples TEXT,
        data_opcao_simples TEXT,
        data_exclusao_simples TEXT,
        opcao_mei TEXT,
        data_opcao_mei TEXT,
        data_exclusao_mei TEXT
    )
    ''')
    
    # Tabela socios
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS socios (
        cnpj TEXT,
        cnpj_basico TEXT,
        identificador_de_socio TEXT,
        nome_socio TEXT,
        cnpj_cpf_socio TEXT,
        qualificacao_socio TEXT,
        data_entrada_sociedade TEXT,
        pais TEXT,
        representante_legal TEXT,
        nome_representante TEXT,
        qualificacao_representante TEXT,
        faixa_etaria TEXT
    )
    ''')
    
    # Criar índices
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_empresas_cnpj_basico ON empresas (cnpj_basico)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_estabelecimento_cnpj ON estabelecimento (cnpj_basico)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_simples_cnpj_basico ON simples (cnpj_basico)')
    
    # Inserir dados de referência
    print("Inserindo dados de referência...")
    
    # Natureza jurídica
    naturezas = [
        ('206-2', 'SOCIEDADE EMPRESÁRIA LIMITADA'),
        ('213-5', 'EMPRESÁRIO (INDIVIDUAL)'),
        ('230-5', 'ASSOCIAÇÃO PRIVADA'),
        ('321-2', 'EMPRESA INDIVIDUAL DE RESPONSABILIDADE LIMITADA (DE NATUREZA EMPRESÁRIA)'),
        ('399-9', 'OUTRAS FORMAS DE EMPRESA INDIVIDUAL DE RESPONSABILIDADE LIMITADA')
    ]
    cursor.executemany("INSERT OR IGNORE INTO natureza_juridica (codigo, descricao) VALUES (?, ?)", naturezas)
    
    # Qualificação de sócios
    qualificacoes = [
        ('05', 'ADMINISTRADOR'),
        ('22', 'SÓCIO'),
        ('49', 'SÓCIO-ADMINISTRADOR'),
        ('10', 'DIRETOR'),
        ('37', 'SÓCIO PESSOA JURÍDICA DOMICILIADO NO EXTERIOR')
    ]
    cursor.executemany("INSERT OR IGNORE INTO qualificacao_socio (codigo, descricao) VALUES (?, ?)", qualificacoes)
    
    # País
    paises = [
        ('076', 'BRASIL'),
        ('249', 'ESTADOS UNIDOS'),
        ('132', 'ARGENTINA'),
        ('245', 'PARAGUAI'),
        ('586', 'URUGUAI')
    ]
    cursor.executemany("INSERT OR IGNORE INTO pais (codigo, descricao) VALUES (?, ?)", paises)
    
    # CNAEs
    cnaes = [
        ('4711-3/02', 'Comércio varejista de mercadorias em geral'),
        ('4713-0/01', 'Lojas de departamentos ou magazines'),
        ('6201-5/00', 'Desenvolvimento de programas de computador sob encomenda'),
        ('7020-4/00', 'Atividades de consultoria em gestão empresarial'),
        ('4120-4/00', 'Construção de edifícios'),
        ('5611-2/01', 'Restaurantes e similares'),
        ('4789-0/99', 'Comércio varejista de outros produtos não especificados anteriormente'),
        ('8630-5/02', 'Atividades de psicologia e psicanálise'),
        ('6920-6/01', 'Atividades jurídicas, exceto cartórios'),
        ('4771-7/01', 'Comércio varejista de produtos farmacêuticos')
    ]
    cursor.executemany("INSERT OR IGNORE INTO cnae (codigo, descricao) VALUES (?, ?)", cnaes)
    
    # Dados para geração
    portes = ['1', '3', '5']  # 1=MICRO, 3=PEQUENO, 5=DEMAIS
    status_simples = ['S', 'N']
    situacoes = ['02', '03', '04', '08']  # ATIVA, SUSPENSA, INAPTA, BAIXADA
    ufs = ['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'GO', 'PE', 'CE', 'PA', 'DF', 'ES', 'PB', 'RN', 'MT']
    
    print("Gerando dados de empresas...")
    
    cnpjs_gerados = set()
    
    for i in range(1500):  # Gerar 1500 empresas
        if i % 100 == 0:
            print(f"Geradas {i} empresas...")
        
        # Gerar CNPJ básico único
        while True:
            cnpj_basico = generate_cnpj_basico()
            if cnpj_basico not in cnpjs_gerados:
                cnpjs_gerados.add(cnpj_basico)
                break
        
        razao_social = fake.company()
        nome_fantasia = razao_social if random.choice([True, False]) else fake.company()
        
        # Inserir na tabela empresas
        empresa_data = (
            cnpj_basico,
            razao_social,
            random.choice(['206-2', '213-5', '321-2']),  # natureza_juridica
            random.choice(['05', '22', '49']),  # qualificacao_responsavel
            str(round(random.uniform(1000, 1000000), 2)),  # capital_social
            random.choice(portes),  # porte_empresa
            ''  # ente_federativo_responsavel
        )
        
        cursor.execute("""
            INSERT INTO empresas (cnpj_basico, razao_social, natureza_juridica, 
                                qualificacao_responsavel, capital_social, porte_empresa, 
                                ente_federativo_responsavel) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, empresa_data)
        
        # Inserir na tabela estabelecimento
        cnpj_ordem = '0001'  # Matriz
        cnpj_dv = str(random.randint(10, 99))
        uf = random.choice(ufs)
        
        estabelecimento_data = (
            cnpj_basico,
            cnpj_ordem,
            cnpj_dv,
            '1',  # matriz
            nome_fantasia,
            random.choice(situacoes),  # situacao_cadastral
            fake.date_between(start_date='-5y', end_date='today').strftime('%Y%m%d'),
            '',  # motivo_situacao_cadastral
            '',  # nome_cidade_exterior
            '076',  # pais (Brasil)
            fake.date_between(start_date='-20y', end_date='today').strftime('%Y%m%d'),
            random.choice(['4711-3/02', '6201-5/00', '7020-4/00']),  # cnae_fiscal_principal
            '',  # cnae_fiscal_secundaria
            'RUA',  # tipo_logradouro
            fake.street_name(),  # logradouro
            str(random.randint(1, 9999)),  # numero
            f'Apto {random.randint(1, 999)}' if random.choice([True, False]) else '',  # complemento
            fake.neighborhood(),  # bairro
            fake.postcode().replace('-', ''),  # cep
            uf,
            str(random.randint(1000, 9999)),  # municipio (código)
            random.choice(['11', '21', '31', '47']),  # ddd_1
            str(random.randint(30000000, 999999999)),  # telefone_1
            '',  # ddd_2
            '',  # telefone_2
            '',  # ddd_fax
            '',  # fax
            generate_email(razao_social),  # correio_eletronico
            '',  # situacao_especial
            ''   # data_situacao_especial
        )
        
        cursor.execute("""
            INSERT INTO estabelecimento (cnpj_basico, cnpj_ordem, cnpj_dv, identificador_matriz_filial,
                                       nome_fantasia, situacao_cadastral, data_situacao_cadastral,
                                       motivo_situacao_cadastral, nome_cidade_exterior, pais,
                                       data_inicio_atividade, cnae_fiscal_principal, cnae_fiscal_secundaria,
                                       tipo_logradouro, logradouro, numero, complemento, bairro, cep,
                                       uf, municipio, ddd_1, telefone_1, ddd_2, telefone_2, ddd_fax,
                                       fax, correio_eletronico, situacao_especial, data_situacao_especial)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, estabelecimento_data)
        
        # Inserir na tabela simples
        opcao_simples = random.choice(status_simples)
        simples_data = (
            cnpj_basico,
            opcao_simples,
            fake.date_between(start_date='-10y', end_date='today').strftime('%Y%m%d') if opcao_simples == 'S' else '',
            '',  # data_exclusao_simples
            random.choice(['S', 'N']),  # opcao_mei
            '',  # data_opcao_mei
            ''   # data_exclusao_mei
        )
        
        cursor.execute("""
            INSERT INTO simples (cnpj_basico, opcao_simples, data_opcao_simples, 
                               data_exclusao_simples, opcao_mei, data_opcao_mei, data_exclusao_mei)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, simples_data)
        
        # Inserir sócios (1-3 sócios por empresa)
        num_socios = random.randint(1, 3)
        for j in range(num_socios):
            cnpj_completo = cnpj_basico + cnpj_ordem + cnpj_dv
            socio_data = (
                cnpj_completo,
                cnpj_basico,
                str(j + 1),  # identificador_de_socio
                fake.name(),  # nome_socio
                str(random.randint(10000000000, 99999999999)),  # cnpj_cpf_socio (CPF)
                random.choice(['05', '22', '49']),  # qualificacao_socio
                fake.date_between(start_date='-20y', end_date='today').strftime('%Y%m%d'),
                '076',  # pais
                '',  # representante_legal
                '',  # nome_representante
                '',  # qualificacao_representante
                str(random.randint(1, 8))  # faixa_etaria
            )
            
            cursor.execute("""
                INSERT INTO socios (cnpj, cnpj_basico, identificador_de_socio, nome_socio,
                                  cnpj_cpf_socio, qualificacao_socio, data_entrada_sociedade,
                                  pais, representante_legal, nome_representante,
                                  qualificacao_representante, faixa_etaria)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, socio_data)
    
    conn.commit()
    
    # Verificar dados inseridos
    cursor.execute("SELECT COUNT(*) FROM empresas")
    empresas_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM estabelecimento")
    estabelecimentos_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM socios")
    socios_count = cursor.fetchone()[0]
    
    print(f"Banco criado com sucesso!")
    print(f"Total de empresas: {empresas_count}")
    print(f"Total de estabelecimentos: {estabelecimentos_count}")
    print(f"Total de sócios: {socios_count}")
    
    # Mostrar algumas amostras
    print("\nAmostra de dados:")
    cursor.execute("""
        SELECT e.cnpj_basico, e.razao_social, est.nome_fantasia, est.uf, s.opcao_simples
        FROM empresas e
        JOIN estabelecimento est ON e.cnpj_basico = est.cnpj_basico
        JOIN simples s ON e.cnpj_basico = s.cnpj_basico
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        print(f"CNPJ: {row[0]} | Empresa: {row[1]} | Fantasia: {row[2]} | UF: {row[3]} | Simples: {row[4]}")
    
    conn.close()
    print(f"\nArquivo salvo em: data/empresas_teste.db")

if __name__ == "__main__":
    create_test_database()
