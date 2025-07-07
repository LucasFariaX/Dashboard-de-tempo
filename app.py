from flask import Flask, render_template, request, redirect, session, flash, jsonify # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
from database import get_db_connection, init_db
from datetime import datetime, date, timedelta
from routes.objetivos import objetivos_bp
from routes.dashboard import dashboard_bp
from routes.habitos import habitos_bp
from routes.agenda import agenda_bp
import sqlite3


app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'
app.register_blueprint(objetivos_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(habitos_bp)
app.register_blueprint(agenda_bp)

# ---- Registros ----

# ✅ REGISTRO COM SENHA CRIPTOGRAFADA
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = generate_password_hash(request.form['senha'])

        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (usuario, senha))
            conn.commit()
            flash('Registro realizado com sucesso!')
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash('Usuário já existe.')
        finally:
            conn.close()

    return render_template('registro.html')

# ✅ LOGIN COM VERIFICAÇÃO DE HASH
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,)).fetchone()
        conn.close()

        if user and check_password_hash(user['senha'], senha):
            session['usuario_id'] = user['id']
            return redirect('/')
        else:
            flash('Usuário ou senha inválidos.')

    return render_template('login.html')

# ✅ PERFIL
@app.route('/perfil')
def perfil():
    if 'usuario_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    usuario = conn.execute("SELECT * FROM usuarios WHERE id = ?", (session['usuario_id'],)).fetchone()
    conn.close()

    tema = session.get('tema', 'claro')
    return render_template('perfil.html', usuario=usuario, tema=tema)

# ✅ ALTERAR SENHA COM VERIFICAÇÃO
@app.route('/alterar_senha', methods=['POST'])
def alterar_senha():
    if 'usuario_id' not in session:
        return redirect('/login')

    senha_atual = request.form['senha_atual']
    nova_senha = request.form['nova_senha']

    conn = get_db_connection()
    usuario = conn.execute("SELECT * FROM usuarios WHERE id = ?", (session['usuario_id'],)).fetchone()

    if not check_password_hash(usuario['senha'], senha_atual):
        flash('Senha atual incorreta.')
        conn.close()
        return redirect('/perfil')

    nova_senha_hash = generate_password_hash(nova_senha)
    conn.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (nova_senha_hash, session['usuario_id']))
    conn.commit()
    conn.close()

    flash('Senha alterada com sucesso!')
    return redirect('/perfil')

# ✅ PREFERÊNCIA DE TEMA
@app.route('/tema', methods=['POST'])
def tema():
    if 'usuario_id' not in session:
        return redirect('/login')

    tema = request.form.get('tema', 'claro')
    session['tema'] = tema
    flash('Tema atualizado com sucesso.')
    return redirect('/perfil')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/')
def home():
    if 'usuario_id' not in session:
        return redirect('/login')
    return render_template('home.html')


# (registro, login, perfil, alterar_senha, tema, logout, home) MANTIDOS COMO ESTÃO


# ---- ANOTAÇÕES ----
@app.route('/anotacoes', methods=['GET', 'POST'])
def anotacoes():
    if 'usuario_id' not in session:
        return redirect('/login')
    conn = get_db_connection()
    if request.method == 'POST':
        conteudo = request.form['conteudo']
        data = datetime.today().strftime('%Y-%m-%d')
        conn.execute('INSERT INTO anotacoes (conteudo, data) VALUES (?, ?)', (conteudo, data))
        conn.commit()
    notas = conn.execute('SELECT * FROM anotacoes ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('anotacoes.html', notas=notas)

@app.route('/anotacoes/editar/<int:id>', methods=['POST'])
def editar_anotacao(id):
    if 'usuario_id' not in session:
        return redirect('/login')
    conteudo = request.form['conteudo']
    conn = get_db_connection()
    conn.execute('UPDATE anotacoes SET conteudo = ? WHERE id = ?', (conteudo, id))
    conn.commit()
    conn.close()
    return redirect('/anotacoes')

@app.route('/anotacoes/excluir/<int:id>', methods=['POST'])
def excluir_anotacao(id):
    if 'usuario_id' not in session:
        return redirect('/login')
    conn = get_db_connection()
    conn.execute('DELETE FROM anotacoes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/anotacoes')

# ---- Objetivos (mantido via blueprint) ----

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
