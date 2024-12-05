from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import os
from werkzeug.utils import secure_filename
from config import DB_CONFIG

# Inicializa a aplicação Flask
app = Flask(__name__)
app.secret_key = "1234"

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

from MySQLdb.cursors import DictCursor

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Captura o parâmetro 'next' para redirecionamento após o login
        next_page = request.args.get('next')  # URL da página original
        
        email = request.form['email']
        senha = request.form['senha']
        cpf_cnpj = request.form['cpf_cnpj']
        
        if len(cpf_cnpj) == 11:  # CPF
            cur = mysql.connection.cursor(DictCursor)
            cur.execute("SELECT id_voluntario, nome, email FROM voluntario WHERE email = %s AND senha_voluntario = %s", (email, senha))
            usuario = cur.fetchone()
            cur.close()

            if usuario:
                session['user_id'] = usuario['id_voluntario']
                session['user_type'] = 'voluntario'
                # Redireciona para a página "next" se existir, ou para o perfil do voluntário
                return redirect(next_page or url_for('perfil'))
            else:
                flash('Email ou senha incorretos.', 'danger')
                return render_template('login.html')
        else:  # CNPJ (ONG)
            cur = mysql.connection.cursor(DictCursor)
            cur.execute("SELECT id_ONG, nome, email FROM ong WHERE email = %s AND senha_ONG = %s", (email, senha))
            usuario = cur.fetchone()
            cur.close()

            if usuario:
                session['user_id'] = usuario['id_ONG']
                session['user_type'] = 'ong'
                # Redireciona para a página "next" se existir, ou para o perfil da ONG
                return redirect(next_page or url_for('perfil_ong'))
            else:
                flash('Email ou senha incorretos.', 'danger')
                return render_template('login.html')

    return render_template('login.html')




@app.route('/perfil', methods=['GET'])
def perfil():
    if 'user_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'danger')
        return redirect('/login')

    user_id = session['user_id']
    cur = mysql.connection.cursor(DictCursor)
    cur.execute("SELECT * FROM voluntario WHERE id_voluntario = %s", (user_id,))
    usuario = cur.fetchone()
    cur.close()

    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect('/login')

    # Consultar histórico de doações feitas pelo voluntário
    cur = mysql.connection.cursor(DictCursor)
    cur.execute("""
        SELECT d.id_Doaçao, o.nome AS nome_ong, n.descricao AS necessidade, d.descricao AS descricao_doaçao
        FROM Doaçao_ONG d
        JOIN ONG o ON d.id_ONG = o.id_ONG
        JOIN Necessidade n ON d.id_Necessidade = n.id_Necessidade
        WHERE d.id_voluntario = %s
    """, (user_id,))

    doacoes = cur.fetchall()
    cur.close()

    return render_template('perfil_voluntario.html', usuario=usuario, doacoes=doacoes)



@app.route('/editar_perfil', methods=['GET', 'POST'])
def editar_perfil():
    if 'user_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'danger')
        return redirect('/login')

    user_id = session['user_id']
    cur = mysql.connection.cursor(DictCursor)
    cur.execute("SELECT * FROM voluntario WHERE id_voluntario = %s", (user_id,))
    usuario = cur.fetchone()
    cur.close()

    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect('/login')

    if request.method == 'POST':
        nome = request.form['nome']
        tipo = request.form['tipo']
        cpf_cnpj = request.form['cpf_cnpj']
        email = request.form['email']
        telefone = request.form['telefone']
        cep = request.form['cep']
        logradouro = request.form['logradouro']
        numero = request.form['numero']
        complemento = request.form.get('complemento', '')
        estado = request.form['estado']

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE voluntario
            SET nome = %s, tipo = %s, cpf_cnpj = %s, email = %s, telefone = %s,
                cep = %s, logradouro = %s, numero = %s, complemento = %s, estado = %s
            WHERE id_voluntario = %s
        """, (nome, tipo, cpf_cnpj, email, telefone, cep, logradouro, numero, complemento, estado, user_id))
        mysql.connection.commit()
        cur.close()

        flash('Perfil atualizado com sucesso!', 'success')
        return redirect('/perfil')

    return render_template('editar_perfil.html', usuario=usuario)

from flask import session, redirect, url_for, flash

@app.route('/logout')
def logout():
    # Remove o ID do usuário da sessão
    session.pop('user_id', None)
    #flash('Você saiu com sucesso.', 'success')
    #return redirect(url_for('login'))  # Redireciona para a tela de login
    return render_template('home.html') # Redireciona para a tela inicial

@app.route('/perfil_ong', methods=['GET'])
def perfil_ong():
    if 'user_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'danger')
        return redirect('/login')

    user_id = session['user_id']
    cur = mysql.connection.cursor(DictCursor)
    
    # Recuperar informações da ONG
    cur.execute("SELECT * FROM ong WHERE id_ONG = %s", (user_id,))
    usuario = cur.fetchone()

    if not usuario:
        cur.close()
        flash('Usuário não encontrado.', 'danger')
        return redirect('/login')

    # Recuperar avaliações relacionadas à ONG
    cur.execute("""
        SELECT a.nota, a.comentario, a.data_avaliacao, v.nome
        FROM avaliacoes a
        INNER JOIN voluntario v ON a.id_voluntario = v.id_voluntario
        WHERE a.id_ONG = %s
        ORDER BY a.data_avaliacao DESC
    """, (user_id,))
    avaliacoes = cur.fetchall()
    cur.close()

    # Passando as informações da ONG e as avaliações para o template
    return render_template('perfil_ong.html', usuario=usuario, avaliacoes=avaliacoes)





@app.route('/editar_perfil_ong', methods=['GET', 'POST'])
def editar_perfil_ong():
    if 'user_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'danger')
        return redirect('/login')

    user_id = session['user_id']
    cur = mysql.connection.cursor(DictCursor)
    cur.execute("SELECT * FROM ong WHERE id_ONG = %s", (user_id,))
    usuario = cur.fetchone()
    cur.close()

    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect('/login')

    # Quando o método for GET, exibe os dados atuais da ONG
    if request.method == 'GET':
        return render_template('editar_perfil_ong.html', usuario=usuario)

    # Quando o método for POST, atualiza os dados da ONG
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        cnpj = request.form['cnpj']
        causa = request.form['causa']
        cep = request.form['cep']
        logradouro = request.form['logradouro']
        numero = request.form['numero']
        complemento = request.form.get('complemento', '')
        estado =request.form['estado']
        cidade =request.form['cidade']
        senha_ONG =request.form['senha_ONG']

        # Atualiza os dados no banco de dados
        cur = mysql.connection.cursor()
        cur.execute(""" 
            UPDATE ong 
            SET nome = %s, email = %s, cnpj = %s, causa = %s, cep = %s, logradouro = %s, 
                numero = %s, complemento = %s, estado = %s, cidade = %s, senha_ONG = %s
            WHERE id_ONG = %s
        """, (nome, email, cnpj, causa, cep, logradouro, numero, complemento, estado, cidade, senha_ONG, user_id))
        mysql.connection.commit()
        cur.close()

        flash('Perfil da ONG atualizado com sucesso!', 'success')
        # Redireciona para a página de perfil da ONG
        return redirect(url_for('perfil_ong'))
    
@app.route('/doaçao/<int:id_ong>', methods=['GET', 'POST'])
def doaçao(id_ong):
    # Verifica se o usuário está logado e é voluntário
    if 'user_id' not in session or session.get('user_type') != 'voluntario':
        flash('Você precisa estar logado como voluntário para fazer uma doação.', 'danger')
        # Redireciona para o login e passa a URL atual como parâmetro "next"
        return redirect(url_for('login', next=request.url))
    
    # Captura o ID do voluntário da sessão
    id_voluntario = session['user_id']

    # Conexão com o banco de dados
    cur = mysql.connection.cursor(DictCursor)
    
    # Busca as necessidades cadastradas
    cur.execute("""
        SELECT id_Necessidade, descricao
        FROM Necessidade
    """)
    necessidades = cur.fetchall()

    # Processa o formulário de doação
    if request.method == 'POST':
        id_necessidade = request.form.get('id_Necessidade')
        descricao = request.form.get('descricao')

        # Insere a doação na tabela
        cur.execute("""
            INSERT INTO Doaçao_ONG (id_ONG, id_voluntario, id_Necessidade, descricao)
            VALUES (%s, %s, %s, %s)
        """, (id_ong, id_voluntario, id_necessidade, descricao))
        mysql.connection.commit()
        cur.close()

        flash('Doação realizada com sucesso!', 'success')
        return redirect(url_for('ongs'))  # Redireciona para a lista de ONGs

    cur.close()
    return render_template('doaçao.html', id_ong=id_ong, necessidades=necessidades)



#@app.route('/perfil')
#def perfil():
   # if 'cpf_cnpj' not in session:
   #     return redirect(url_for('login'))
    
   # cpf_cnpj = session['cpf_cnpj']
#    user_type = session['user_type']

#    if user_type == 'ong':
#        usuario = ONG.query.get(user_id)
#        return render_template('perfil_ong.html', usuario=usuario)
#    elif user_type == 'voluntario':
#        usuario = voluntario.query.get(user_id)
#       return render_template('perfil_voluntario.html', usuario=usuario)
    
    #return cpf_cnpj, 200
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
