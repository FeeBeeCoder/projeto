from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from config import DB_CONFIG

# Inicializa a aplicação Flask
app = Flask(__name__)

# Configuração do banco de dados a partir do arquivo config.py
app.config['MYSQL_HOST'] = DB_CONFIG['MYSQL_HOST']
app.config['MYSQL_USER'] = DB_CONFIG['MYSQL_USER']
app.config['MYSQL_PASSWORD'] = DB_CONFIG['MYSQL_PASSWORD']
app.config['MYSQL_DB'] = DB_CONFIG['MYSQL_DB']

# Inicializa a conexão MySQL com a aplicação Flask
mysql = MySQL(app)

# Rota para a página inicial (home)
@app.route('/')
def home():
    return render_template('home.html')

# Rota para a página de ONGs
@app.route('/ongs')
def ongs():
    return render_template('ongs.html')

# Rota para a página de oportunidades
@app.route('/oportunidades')
def oportunidades():
    return render_template('oportunidades.html')

# Rota para a galeria
@app.route('/galeria')
def galeria():
    return render_template('galeria.html')

# Rota para a página de contato
@app.route('/contato')
def contato():
    return render_template('contato.html')

# Rota para a página de cadastro 
@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

# Rota para a página de login
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/cadastrar_ong', methods=['GET', 'POST'])
def cadastrar_ong():
    if request.method == 'POST':
        nome = request.form['nome']
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

        # Inserir no banco de dados
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO ong (nome, cnpj, causa, id_Necessidade, cep, logradouro, numero, complemento, estado, cidade, senha_ONG)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nome, cnpj, causa, id_necessidade, cep, logradouro, numero, complemento, estado, cidade, senha_ONG))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('ongs'))

    return render_template('cadastrar_ong.html')


@app.route('/cadastrar_voluntario', methods=['POST'])
def cadastrar_voluntario():
    # Capturar os dados do formulário de voluntário e salvar no banco de dados
    pass


if __name__ == '__main__':
    app.run(debug=True)