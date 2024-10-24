# app.py

from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from config import DB_CONFIG
# Importa as bibliotecas necessárias: Flask para criar a aplicação web, MySQL para conexão com o banco de dados,
# e DB_CONFIG do arquivo de configuração.

app = Flask(__name__)
# Inicializa a aplicação Flask.

# Configuração do banco de dados
app.config['MYSQL_HOST'] = DB_CONFIG['MYSQL_HOST']
app.config['MYSQL_USER'] = DB_CONFIG['MYSQL_USER']
app.config['MYSQL_PASSWORD'] = DB_CONFIG['MYSQL_PASSWORD']
app.config['MYSQL_DB'] = DB_CONFIG['MYSQL_DB']
# Carrega as configurações do banco de dados do dicionário DB_CONFIG definido no arquivo config.py.

# Inicializando o MySQL
mysql = MySQL(app)
# Inicializa a conexão com o banco de dados MySQL utilizando as configurações fornecidas.

# Página inicial (home)
@app.route('/')
def home():
    return render_template('home.html')
# Define a rota para a página inicial ('/'). A função 'home' renderiza o template 'home.html'.

# Página inicial do CRUD (listar contatos)
@app.route('/contatos/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM contatos")
    contatos = cur.fetchall()  # Retorna tuplas
    cur.close()
    return render_template('contatos/index.html', contatos=contatos)
# Define a rota para listar os contatos ('/contatos/'). A função 'index' obtém todos os contatos do banco de dados
# e os passa para o template 'index.html' para serem exibidos.

# Adicionar contato
@app.route('/contatos/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO contatos (nome, telefone) VALUES (%s, %s)", (nome, telefone))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('index'))
    
    return render_template('contatos/add.html')
# Define a rota para adicionar contatos ('/contatos/add'). Se o método de requisição for POST,
# os dados do formulário (nome e telefone) são obtidos e inseridos no banco de dados.
# Se for uma requisição GET, o template 'add.html' é renderizado para o formulário de adição.

# Editar contato
@app.route('/contatos/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM contatos WHERE id = %s", (id,))
    contato = cur.fetchone()  # Retorna tupla
    cur.close()
    
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        
        cur = mysql.connection.cursor()
        cur.execute("UPDATE contatos SET nome = %s, telefone = %s WHERE id = %s", (nome, telefone, id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('index'))
    
    return render_template('contatos/edit.html', contato=contato)
# Define a rota para editar contatos ('/contatos/edit/<int:id>'). O ID do contato é passado na URL.
# A função busca os dados do contato pelo ID e os exibe no formulário de edição.
# Se for uma requisição POST, atualiza os dados do contato no banco de dados.

# Deletar contato
@app.route('/contatos/delete/<int:id>')
def delete(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM contatos WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('index'))
# Define a rota para deletar contatos ('/contatos/delete/<int:id>'). O ID do contato é passado na URL,
# e a função deleta o contato correspondente do banco de dados.

if __name__ == '__main__':
    app.run(debug=True)
# Inicia o servidor Flask em modo de depuração (debug). Esse bloco garante que a aplicação será executada
# apenas quando o arquivo app.py for executado diretamente, e não importado como módulo.
