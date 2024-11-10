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

# Página inicial (home)
@app.route('/')
def home():
    return render_template('home.html')

# Listagem de contatos (CRUD)
@app.route('/contatos/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM contatos")
    contatos = cur.fetchall()  # Busca todos os registros da tabela de contatos
    cur.close()
    return render_template('contatos/index.html', contatos=contatos)

# Adicionar contato
@app.route('/contatos/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']

        # Insere os dados no banco de dados
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO contatos (nome, telefone) VALUES (%s, %s)", (nome, telefone))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('index'))

    return render_template('contatos/add.html')

# Editar contato
@app.route('/contatos/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM contatos WHERE id = %s", (id,))
    contato = cur.fetchone()  # Obtém os dados do contato específico
    cur.close()

    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']

        # Atualiza os dados no banco de dados
        cur = mysql.connection.cursor()
        cur.execute("UPDATE contatos SET nome = %s, telefone = %s WHERE id = %s", (nome, telefone, id))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('index'))

    return render_template('contatos/edit.html', contato=contato)

# Deletar contato
@app.route('/contatos/delete/<int:id>')
def delete(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM contatos WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('index'))

# Executa a aplicação no modo debug
if __name__ == '__main__':
    app.run(debug=True)
