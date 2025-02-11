from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# Função para conectar ao banco de dados
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Rota principal
@app.route('/')
def index():
    conn = get_db_connection()
    
    # Buscar objetivos
    objetivos = conn.execute('SELECT * FROM objetivos').fetchall()

    # Para cada objetivo, buscar suas tarefas
    objetivos_com_tarefas = []
    for objetivo in objetivos:
        tarefas = conn.execute('SELECT * FROM tarefas WHERE objetivo_id = ?', (objetivo['id'],)).fetchall()
        
        # Transformando cada objetivo em um dicionário e adicionando as tarefas
        objetivo_dict = dict(objetivo)
        objetivo_dict['tarefas'] = [dict(tarefa) for tarefa in tarefas]
        
        objetivos_com_tarefas.append(objetivo_dict)

    conn.close()
    return render_template('index.html', objetivos=objetivos_com_tarefas)

# Rota para criar um novo objetivo
@app.route('/criar_objetivo', methods=['POST'])
def criar_objetivo():
    nome = request.form['nome']
    meta = int(request.form['meta'])
    
    if meta <= 0:
        flash('A meta deve ser maior que zero.', 'error')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    conn.execute('INSERT INTO objetivos (nome, meta) VALUES (?, ?)', (nome, meta))
    conn.commit()
    conn.close()
    
    flash('Objetivo criado com sucesso!', 'success')
    return redirect(url_for('index'))

# Rota para registrar entrada
@app.route('/registrar_entrada/<int:objetivo_id>')
def registrar_entrada(objetivo_id):
    entrada = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    conn = get_db_connection()
    conn.execute('INSERT INTO pontos (objetivo_id, entrada) VALUES (?, ?)', (objetivo_id, entrada))
    conn.commit()
    conn.close()
    
    flash('Entrada registrada com sucesso!', 'success')
    return redirect(url_for('index'))

# Rota para registrar saída
@app.route('/registrar_saida/<int:objetivo_id>')
def registrar_saida(objetivo_id):
    saida = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    conn = get_db_connection()
    ponto = conn.execute('SELECT id, entrada FROM pontos WHERE objetivo_id = ? AND saida IS NULL ORDER BY entrada DESC LIMIT 1', (objetivo_id,)).fetchone()
    
    if ponto:
        try:
            entrada_dt = datetime.strptime(ponto['entrada'], '%Y-%m-%d %H:%M:%S')
            saida_dt = datetime.strptime(saida, '%Y-%m-%d %H:%M:%S')
            tempo_gasto = int((saida_dt - entrada_dt).total_seconds() / 3600)  # Horas
            
            conn.execute('UPDATE pontos SET saida = ? WHERE id = ?', (saida, ponto['id']))
            conn.execute('UPDATE objetivos SET progresso = progresso + ? WHERE id = ?', (tempo_gasto, objetivo_id))
            conn.commit()
            conn.close()
            
            flash('Saída registrada com sucesso!', 'success')
        except Exception as e:
            conn.close()
            flash(f'Erro ao registrar saída: {str(e)}', 'error')
    else:
        conn.close()
        flash('Nenhuma entrada pendente encontrada.', 'error')
    
    return redirect(url_for('index'))

# Rota para editar um objetivo
@app.route('/editar_objetivo/<int:objetivo_id>', methods=['GET', 'POST'])
def editar_objetivo(objetivo_id):
    if request.method == 'POST':
        nome = request.form['nome']
        meta = int(request.form['meta'])
        
        if meta <= 0:
            flash('A meta deve ser maior que zero.', 'error')
            return redirect(url_for('editar_objetivo', objetivo_id=objetivo_id))
        
        conn = get_db_connection()
        conn.execute('UPDATE objetivos SET nome = ?, meta = ? WHERE id = ?', (nome, meta, objetivo_id))
        conn.commit()
        conn.close()
        
        flash('Objetivo atualizado com sucesso!', 'success')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    objetivo = conn.execute('SELECT * FROM objetivos WHERE id = ?', (objetivo_id,)).fetchone()
    conn.close()
    
    return render_template('editar_objetivo.html', objetivo=objetivo)

# Rota para excluir um objetivo
@app.route('/excluir_objetivo/<int:objetivo_id>')
def excluir_objetivo(objetivo_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM objetivos WHERE id = ?', (objetivo_id,))
    conn.execute('DELETE FROM pontos WHERE objetivo_id = ?', (objetivo_id,))
    conn.commit()
    conn.close()
    
    flash('Objetivo excluído com sucesso!', 'success')
    return redirect(url_for('index'))

# Rota para visualizar registros de pontos
@app.route('/registros/<int:objetivo_id>')
def registros(objetivo_id):
    conn = get_db_connection()
    pontos = conn.execute('SELECT * FROM pontos WHERE objetivo_id = ?', (objetivo_id,)).fetchall()
    objetivo = conn.execute('SELECT * FROM objetivos WHERE id = ?', (objetivo_id,)).fetchone()
    conn.close()
    
    if not objetivo:
        flash('Objetivo não encontrado.', 'error')
        return redirect(url_for('index'))
    
    return render_template('registros.html', pontos=pontos, objetivo=objetivo, datetime=datetime)


# Rota para fornecer os dados para os gráficos
from flask import jsonify

@app.route('/dados_graficos')
def dados_graficos():
    conn = get_db_connection()
    objetivos = conn.execute('SELECT nome, meta, progresso FROM objetivos').fetchall()
    conn.close()

    dados = {
        "objetivos": [objetivo["nome"] for objetivo in objetivos],
        "metas": [objetivo["meta"] for objetivo in objetivos],
        "progresso": [objetivo["progresso"] for objetivo in objetivos],
    }
    
    return jsonify(dados)


# Rota para adicionar uma nova tarefa a um objetivo
@app.route('/adicionar_tarefa/<int:objetivo_id>', methods=['POST'])
def adicionar_tarefa(objetivo_id):
    descricao = request.form['descricao']

    if not descricao.strip():
        flash('A tarefa não pode estar vazia.', 'error')
        return redirect(url_for('index'))

    conn = get_db_connection()
    conn.execute('INSERT INTO tarefas (objetivo_id, descricao) VALUES (?, ?)', (objetivo_id, descricao))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

# Rota para marcar uma tarefa como concluída ou não
@app.route('/marcar_concluida/<int:tarefa_id>', methods=['POST'])
def marcar_concluida(tarefa_id):
    concluida = request.form.get('concluida', '0')

    conn = get_db_connection()
    conn.execute('UPDATE tarefas SET concluida = ? WHERE id = ?', (concluida, tarefa_id))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

# Rota para excluir uma tarefa
@app.route('/excluir_tarefa/<int:tarefa_id>', methods=['POST'])
def excluir_tarefa(tarefa_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tarefas WHERE id = ?', (tarefa_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)