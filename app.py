from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import os
from werkzeug.utils import secure_filename
from config import DB_CONFIG

# Inicializa a aplicação Flask
app = Flask(__name__)

# Configuração do banco de dados
app.config['MYSQL_HOST'] = DB_CONFIG['MYSQL_HOST']
app.config['MYSQL_USER'] = DB_CONFIG['MYSQL_USER']
app.config['MYSQL_PASSWORD'] = DB_CONFIG['MYSQL_PASSWORD']
app.config['MYSQL_DB'] = DB_CONFIG['MYSQL_DB']

# Configuração para uploads
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Função para verificar se o arquivo tem extensão permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Inicializa a conexão MySQL com a aplicação Flask
mysql = MySQL(app)

# Rota para a página de ONGs
@app.route('/ongs', methods=['GET'])
def ongs():
    # Captura os filtros enviados pelo formulário
    causa = request.args.get('causa', '')
    necessidade = request.args.get('necessidade', '')
    estado = request.args.get('estado', '')

    # Query base para listar ONGs
    query = """
        SELECT ong.id_ONG, ong.nome, ong.causa, ong.cidade, ong.estado, ong.logo, necessidade.tipo
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

    # Executa a query para listar as ONGs
    cur = mysql.connection.cursor()
    cur.execute(query, params)
    ongs = cur.fetchall()

    # Recupera as causas disponíveis
    cur.execute("SELECT DISTINCT causa FROM ong")
    causas = cur.fetchall()

    # Recupera os tipos de necessidade disponíveis
    cur.execute("SELECT DISTINCT tipo FROM necessidade")
    necessidades = cur.fetchall()

    cur.close()

    return render_template('ongs.html', ongs=ongs, causas=causas, necessidades=necessidades)


# Outras rotas permanecem inalteradas
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/oportunidades')
def oportunidades():
    return render_template('oportunidades.html')

@app.route('/galeria')
def galeria():
    return render_template('galeria.html')

@app.route('/contato')
def contato():
    return render_template('contato.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/login')
def login():
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

@app.route('/atualizar_logo', methods=['POST'])
def atualizar_logo():
    if request.method == 'POST':
        id_ONG = request.form['id_ONG']
        logo = request.files['logo']

        # Verifica se o arquivo enviado é válido
        if logo and allowed_file(logo.filename):
            filename = secure_filename(logo.filename)
            logo_path = os.path.join('uploads', filename)
            logo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Atualiza o caminho da logo no banco de dados
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE ong
                SET logo = %s
                WHERE id_ONG = %s
            """, (logo_path, id_ONG))
            mysql.connection.commit()
            cur.close()

            return redirect(url_for('ongs'))
        else:
            return "Arquivo inválido. Por favor, envie uma imagem no formato permitido (png, jpg, jpeg, gif)."

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

@app.route('/avaliar_ong/<int:id_ong>', methods=['GET', 'POST'])
def avaliar_ong(id_ong):
    if request.method == 'POST':
        cpf_cnpj = request.form['cpf_cnpj']
        senha = request.form['senha']
        nota = request.form['nota']
        comentario = request.form['comentario']

        # Verifica se o CPF/CNPJ e senha correspondem a um voluntário válido
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id_voluntario
            FROM voluntario
            WHERE cpf_cnpj = %s AND senha_voluntario = %s
        """, (cpf_cnpj, senha))
        voluntario = cur.fetchone()
        cur.close()

        if voluntario:
            id_voluntario = voluntario[0]

            # Inserir avaliação no banco de dados
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO avaliacoes (id_ONG, id_voluntario, nota, comentario)
                VALUES (%s, %s, %s, %s)
            """, (id_ong, id_voluntario, nota, comentario))
            mysql.connection.commit()
            cur.close()

            return redirect(url_for('ongs'))
        else:
            return "CPF/CNPJ ou senha inválidos."

    # Recuperar detalhes da ONG
    cur = mysql.connection.cursor()
    cur.execute("SELECT nome FROM ong WHERE id_ONG = %s", (id_ong,))
    ong = cur.fetchone()
    cur.close()
    return render_template('avaliar_ong.html', ong=ong)

@app.route('/avaliacoes/<int:id_ong>')
def avaliacoes(id_ong):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT a.nota, a.comentario, a.data_avaliacao, v.nome
        FROM avaliacoes a
        INNER JOIN voluntario v ON a.id_voluntario = v.id_voluntario
        WHERE a.id_ONG = %s
        ORDER BY a.data_avaliacao DESC
    """, (id_ong,))
    avaliacoes = cur.fetchall()
    cur.close()
    
    # Recuperar detalhes da ONG
    cur = mysql.connection.cursor()
    cur.execute("SELECT nome FROM ong WHERE id_ONG = %s", (id_ong,))
    ong = cur.fetchone()
    cur.close()
    
    return render_template('avaliacoes.html', avaliacoes=avaliacoes, ong=ong)

if __name__ == '__main__':
    app.run(debug=True)
