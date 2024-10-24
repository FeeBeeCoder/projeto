from flask import Flask, render_template

app = Flask(__name__)

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

# Rota para a página de cadastro de ONGs
@app.route('/cadastrar_ong')
def cadastrar_ong():
    return render_template('cadastrar_ong.html')

# Rota para a página de login
@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
