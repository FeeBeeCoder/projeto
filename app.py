from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error
import os
from werkzeug.utils import secure_filename

# Configuração do banco de dados
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'ECU73!#V',
    'database': 'projetopi',
    'auth_plugin': 'mysql_native_password'
}

# Inicializa a aplicação Flask
app = Flask(__name__)

# Configuração para uploads
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Função para verificar se o arquivo tem extensão permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Função para criar conexão com o banco de dados
def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

# Rota para a página inicial
@app.route('/')
def home():
    return render_template('home.html')

# Rota para a página de ONGs
@app.route('/ongs', methods=['GET'])
def ongs():
    connection = get_db_connection()
    if not connection:
        return "Erro ao conectar ao banco de dados.", 500

    cursor = connection.cursor(dictionary=True)

    # Captura os filtros enviados pelo formulário
    causa = request.args.get('causa', '')
    necessidade = request.args.get('necessidade', '')
    estado = request.args.get('estado', '')

    # Query base para listar ONGs
    query = """
        SELECT ong.id_ONG, ong.nome, ong.causa, ong.cidade, ong.estado, ong.logo, 
               necessidade.tipo, ong.telefone, ong.celular
        FROM ong
        LEFT JOIN necessidade ON ong.id_Necessidade = necessidade.id_Necessidade
        WHERE 1=1
    """
    params = []

    # Adiciona filtros, se aplicáveis
    if causa:
        query += " AND ong.causa = %s"
        params.append(causa)

    if necessidade:
        query += " AND necessidade.tipo = %s"
        params.append(necessidade)

    if estado:
        query += " AND ong.estado = %s"
        params.append(estado)

    try:
        cursor.execute(query, params)
        ongs = cursor.fetchall()
        
        # Recupera as causas disponíveis
        cursor.execute("SELECT DISTINCT causa FROM ong")
        causas = cursor.fetchall()

        # Recupera os tipos de necessidade disponíveis
        cursor.execute("SELECT DISTINCT tipo FROM necessidade")
        necessidades = cursor.fetchall()

    except Error as e:
        print(f"Erro ao executar a query: {e}")
        return "Erro ao buscar dados do banco de dados.", 500
    finally:
        cursor.close()
        connection.close()

    # Renderiza o template com os dados
    return render_template('ongs.html', ongs=ongs, causas=causas, necessidades=necessidades)

# Rota para oportunidades
@app.route('/oportunidades')
def oportunidades():
    return render_template('oportunidades.html')

# Rota para galeria
@app.route('/galeria')
def galeria():
    return render_template('galeria.html')

# Rota para contato
@app.route('/contato')
def contato():
    return render_template('contato.html')

# Rota para cadastro
@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

# Rota para recuperar senha
@app.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    connection = get_db_connection()
    if not connection:
        return "Erro ao conectar ao banco de dados.", 500

    if request.method == 'POST':
        email = request.form.get('email')
        cursor = connection.cursor()
        try:
            cursor.execute(
                "SELECT email FROM voluntario WHERE email = %s UNION SELECT email FROM ong WHERE email = %s",
                (email, email)
            )
            user = cursor.fetchone()
        except Error as e:
            print(f"Erro ao buscar e-mails: {e}")
            return "Erro ao processar sua solicitação.", 500
        finally:
            cursor.close()
            connection.close()

        if user:
            return "Um e-mail para redefinição de senha foi enviado.", 200
        else:
            return "E-mail não encontrado.", 404

    return render_template('recuperar_senha.html')

# Rota para login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Recupera os dados do formulário
        email = request.form.get('email')
        senha = request.form.get('senha')

        # Valida se os campos estão preenchidos
        if not email or not senha:
            return "Por favor, preencha todos os campos.", 400

        # Conecta ao banco de dados
        connection = get_db_connection()
        if not connection:
            return "Erro ao conectar ao banco de dados.", 500

        cursor = connection.cursor(dictionary=True)
        try:
            # Consulta no banco para verificar o usuário
            cursor.execute(
                "SELECT * FROM usuarios WHERE email = %s AND senha = %s",
                (email, senha)
            )
            user = cursor.fetchone()

        except Error as e:
            print(f"Erro ao buscar usuário: {e}")
            return "Erro interno ao processar a solicitação.", 500
        finally:
            cursor.close()
            connection.close()

        # Verifica se o usuário existe
        if user:
            # Redireciona para a página inicial após login bem-sucedido
            return redirect(url_for('home'))
        else:
            return "Credenciais inválidas.", 401

    # Caso o método seja GET, exibe o formulário de login
    return render_template('login.html')

@app.route('/avaliar_ong/<int:id_ong>', methods=['GET', 'POST'])
def avaliar_ong(id_ong):
    connection = get_db_connection()
    if not connection:
        return "Erro ao conectar ao banco de dados.", 500

    if request.method == 'POST':
        cpf_cnpj = request.form['cpf_cnpj']
        senha = request.form['senha']
        nota = request.form['nota']
        comentario = request.form['comentario']

        cursor = connection.cursor(dictionary=True)

        try:
            # Verifica se o voluntário existe
            cursor.execute("""
                SELECT id_voluntario
                FROM voluntario
                WHERE cpf_cnpj = %s AND senha_voluntario = %s
            """, (cpf_cnpj, senha))
            voluntario = cursor.fetchone()

            if not voluntario:
                return "CPF/CNPJ ou senha inválidos.", 401

            # Insere a avaliação no banco de dados
            cursor.execute("""
                INSERT INTO avaliacoes (id_ONG, id_voluntario, nota, comentario)
                VALUES (%s, %s, %s, %s)
            """, (id_ong, voluntario['id_voluntario'], nota, comentario))
            connection.commit()

            return redirect(url_for('avaliacoes', id_ong=id_ong))

        except Error as e:
            print(f"Erro ao salvar avaliação: {e}")
            return "Erro interno ao processar a solicitação.", 500

        finally:
            cursor.close()
            connection.close()

    else:
        cursor = connection.cursor(dictionary=True)
        try:
            # Busca informações da ONG
            cursor.execute("SELECT nome FROM ong WHERE id_ONG = %s", (id_ong,))
            ong = cursor.fetchone()

            if not ong:
                return "ONG não encontrada.", 404

            return render_template('avaliar_ong.html', ong=ong)

        except Error as e:
            print(f"Erro ao buscar informações da ONG: {e}")
            return "Erro interno ao buscar informações da ONG.", 500

        finally:
            cursor.close()
            connection.close()

        
@app.route('/avaliacoes/<int:id_ong>')
def avaliacoes(id_ong):
    connection = get_db_connection()
    if not connection:
        return "Erro ao conectar ao banco de dados.", 500

    cursor = connection.cursor(dictionary=True)

    try:
        # Buscando avaliações
        cursor.execute("""
            SELECT a.nota, a.comentario, a.data_avaliacao, v.nome AS nome_voluntario
            FROM avaliacoes a
            INNER JOIN voluntario v ON a.id_voluntario = v.id_voluntario
            WHERE a.id_ONG = %s
            ORDER BY a.data_avaliacao DESC
        """, (id_ong,))
        avaliacoes = cursor.fetchall()

        # Buscando informações da ONG
        cursor.execute("SELECT nome FROM ong WHERE id_ONG = %s", (id_ong,))
        ong = cursor.fetchone()

    except Error as e:
        print(f"Erro ao buscar avaliações: {e}")
        return "Erro ao processar a solicitação.", 500
    finally:
        cursor.close()
        connection.close()

    return render_template('avaliacoes.html', avaliacoes=avaliacoes, ong=ong)



@app.route('/cadastrar_voluntario', methods=['GET', 'POST'])
def cadastrar_voluntario():
    if request.method == 'POST':
        nome = request.form['nome']
        tipo = request.form['tipo']
        cpf_cnpj = request.form['cpf_cnpj']
        email = request.form.get('email', '')
        telefone = request.form.get('telefone', '')
        cep = request.form['cep']
        logradouro = request.form['logradouro']
        numero = request.form['numero']
        complemento = request.form.get('complemento', '')
        estado = request.form['estado']
        cidade = request.form['cidade']
        senha_voluntario = request.form['senha_voluntario']

        # Inserir no banco de dados
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO voluntario (nome, tipo, cpf_cnpj, email, telefone, cep, logradouro, numero, complemento, estado, cidade, senha_voluntario)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nome, tipo, cpf_cnpj, email, telefone, cep, logradouro, numero, complemento, estado, cidade, senha_voluntario))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('cadastrar_voluntario'))
    return render_template('login.html')

        
@app.route('/cadastrar_ong', methods=['GET', 'POST'])
def cadastrar_ong():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        cnpj = request.form['cnpj']
        causa = request.form['causa']
        id_necessidade = request.form['id_Necessidade']
        cep = request.form['cep']
        logradouro = request.form['logradouro']
        numero = request.form['numero']
        complemento = request.form.get('complemento', '')
        estado = request.form['estado']
        cidade = request.form['cidade']
        senha_ONG = request.form['senha_ONG']

        # Gerenciar upload do arquivo
        logo = request.files['logo']
        logo_path = ''
        if logo and allowed_file(logo.filename):
            filename = secure_filename(logo.filename)
            logo_path = os.path.join('uploads', filename)
            logo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Inserir no banco de dados
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO ong (nome, email, cnpj, causa, id_Necessidade, cep, logradouro, numero, complemento, estado, cidade, senha_ONG, logo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nome, email, cnpj, causa, id_necessidade, cep, logradouro, numero, complemento, estado, cidade, senha_ONG, logo_path))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('ongs'))
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
