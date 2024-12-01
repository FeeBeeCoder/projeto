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

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email = %s AND senha = %s", (email, senha))
        user = cur.fetchone()
        cur.close()

        if user:
            return redirect(url_for('home'))
        else:
            return "Credenciais inválidas.", 401

    return render_template('login.html')

@app.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'POST':
        email = request.form.get('email')

        cur = mysql.connection.cursor()
        cur.execute("SELECT email FROM usuarios WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user:
            return "Um e-mail para redefinição de senha foi enviado.", 200
        else:
            return "E-mail não encontrado.", 404

    return render_template('recuperar_senha.html')

@app.route('/cadastrar_ong', methods=['GET', 'POST'])
def cadastrar_ong():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        celular = request.form['celular']
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

        # Validações
        if not nome or not email or not telefone or not celular or not cnpj or not causa or not id_necessidade:
            return "Por favor, preencha todos os campos obrigatórios.", 400

        logo = request.files['logo']
        logo_path = ''
        if logo and allowed_file(logo.filename):
            filename = secure_filename(logo.filename)
            logo_path = f"uploads/{filename}"
            logo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO ong (nome, email, telefone, celular, cnpj, causa, id_Necessidade, cep, logradouro, numero, complemento, estado, cidade, senha_ONG, logo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nome, email, telefone, celular, cnpj, causa, id_necessidade, cep, logradouro, numero, complemento, estado, cidade, senha_ONG, logo_path))
        mysql.connection.commit()

        # Alimenta a tabela de usuários
        cur.execute("INSERT INTO usuarios (email, senha, tipo) VALUES (%s, %s, %s)", (email, senha_ONG, 'ONG'))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('ongs'))
    return render_template('login.html')

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

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO voluntario (nome, tipo, cpf_cnpj, email, telefone, cep, logradouro, numero, complemento, estado, cidade, senha_voluntario)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nome, tipo, cpf_cnpj, email, telefone, cep, logradouro, numero, complemento, estado, cidade, senha_voluntario))
        mysql.connection.commit()

        # Alimenta a tabela de usuários
        cur.execute("INSERT INTO usuarios (email, senha, tipo) VALUES (%s, %s, %s)", (email, senha_voluntario, 'Voluntário'))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('cadastrar_voluntario'))
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
