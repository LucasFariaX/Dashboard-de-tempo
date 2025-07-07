from flask import Blueprint, render_template, request, redirect, flash, session, jsonify
import sqlite3
from datetime import datetime, date, timedelta

objetivos_bp = Blueprint('objetivos', __name__)

def get_db_connection():
    conn = sqlite3.connect('rotina.db')
    conn.row_factory = sqlite3.Row
    return conn

def calcular_dias_restantes(data_final):
    hoje = date.today()
    data_final_dt = datetime.strptime(data_final, '%Y-%m-%d').date()
    return (data_final_dt - hoje).days

@objetivos_bp.route('/objetivos')
def objetivos():
    if 'usuario_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    objetivos_raw = conn.execute("SELECT * FROM objetivos").fetchall()
    objetivos = []
    hoje = date.today()

    for obj in objetivos_raw:
        tarefas = conn.execute("SELECT * FROM tarefas WHERE objetivo_id = ?", (obj["id"],)).fetchall()
        marcacoes = conn.execute("SELECT * FROM objetivo_marcacoes WHERE objetivo_id = ? ORDER BY data DESC LIMIT 7", (obj["id"],)).fetchall()

        # Consistência dos últimos 30 dias
        inicio_periodo = hoje - timedelta(days=30)
        dias_marcados = conn.execute("""
            SELECT COUNT(*) FROM objetivo_marcacoes 
            WHERE objetivo_id = ? AND data >= ?
        """, (obj["id"], inicio_periodo.strftime('%Y-%m-%d'))).fetchone()[0]
        porcentagem_consistencia = int((dias_marcados / 30) * 100)

        objetivos.append({
            "id": obj["id"],
            "nome": obj["nome"],
            "data_final": obj["data_final"],
            "data_conclusao": obj["data_conclusao"],
            "dias_restantes": calcular_dias_restantes(obj["data_final"]),
            "tarefas": tarefas,
            "marcacoes": marcacoes,
            "consistencia": porcentagem_consistencia
        })

    conn.close()
    return render_template("objetivos.html", objetivos=objetivos, calcular_dias_restantes=calcular_dias_restantes)

@objetivos_bp.route('/objetivos/criar', methods=['POST'])
def criar_objetivo():
    nome = request.form['nome']
    data_final = request.form['data_final']

    conn = get_db_connection()
    conn.execute("INSERT INTO objetivos (nome, data_final) VALUES (?, ?)", (nome, data_final))
    conn.commit()
    conn.close()

    flash("🎯 Objetivo criado com sucesso!", "success")
    return redirect('/objetivos')

@objetivos_bp.route('/objetivos/concluir/<int:id>', methods=['POST'])
def concluir_objetivo(id):
    data_conclusao = datetime.today().strftime('%Y-%m-%d')
    conn = get_db_connection()
    conn.execute("UPDATE objetivos SET data_conclusao = ? WHERE id = ?", (data_conclusao, id))
    conn.commit()
    conn.close()

    flash("✅ Objetivo marcado como concluído.", "success")
    return redirect('/objetivos')

@objetivos_bp.route('/adicionar_tarefa/<int:objetivo_id>', methods=['POST'])
def adicionar_tarefa(objetivo_id):
    descricao = request.form['descricao']
    conn = get_db_connection()
    conn.execute("INSERT INTO tarefas (objetivo_id, descricao) VALUES (?, ?)", (objetivo_id, descricao))
    conn.commit()
    conn.close()

    flash("✅ Tarefa adicionada!", "success")
    return redirect('/objetivos')

@objetivos_bp.route('/marcar_concluida/<int:tarefa_id>', methods=['POST'])
def marcar_concluida(tarefa_id):
    conn = get_db_connection()
    tarefa = conn.execute("SELECT concluida FROM tarefas WHERE id = ?", (tarefa_id,)).fetchone()
    novo_estado = 0 if tarefa["concluida"] else 1
    conn.execute("UPDATE tarefas SET concluida = ? WHERE id = ?", (novo_estado, tarefa_id))
    conn.commit()
    conn.close()

    flash("📌 Tarefa atualizada!", "info")
    return redirect('/objetivos')

@objetivos_bp.route('/excluir_tarefa/<int:tarefa_id>', methods=['POST'])
def excluir_tarefa(tarefa_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
    conn.commit()
    conn.close()

    flash("🗑️ Tarefa excluída.", "danger")
    return redirect('/objetivos')

@objetivos_bp.route('/excluir_objetivo/<int:id>')
def excluir_objetivo(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM tarefas WHERE objetivo_id = ?", (id,))
    conn.execute("DELETE FROM objetivo_marcacoes WHERE objetivo_id = ?", (id,))
    conn.execute("DELETE FROM objetivos WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    flash("🚫 Objetivo excluído com sucesso.", "danger")
    return redirect('/objetivos')

@objetivos_bp.route('/objetivos/marcar/<int:id>', methods=['POST'])
def marcar_progresso(id):
    hoje = datetime.today().strftime('%Y-%m-%d')
    observacao = request.form.get('observacao')

    conn = get_db_connection()
    ja_marcado = conn.execute("""
        SELECT COUNT(*) FROM objetivo_marcacoes 
        WHERE objetivo_id = ? AND data = ?
    """, (id, hoje)).fetchone()[0]

    if ja_marcado == 0:
        conn.execute("""
            INSERT INTO objetivo_marcacoes (objetivo_id, data, observacao) 
            VALUES (?, ?, ?)
        """, (id, hoje, observacao))
        conn.commit()
        flash("📌 Progresso de hoje registrado!", "success")
    else:
        flash("⚠️ Progresso de hoje já registrado.", "warning")

    conn.close()
    return redirect('/objetivos')

@objetivos_bp.route('/dados_graficos')
def dados_graficos():
    conn = get_db_connection()
    objetivos = conn.execute("SELECT nome, data_final FROM objetivos WHERE data_conclusao IS NULL").fetchall()
    conn.close()

    hoje = date.today()
    nomes = []
    dias_restantes = []

    for o in objetivos:
        nomes.append(o["nome"])
        dias = (datetime.strptime(o["data_final"], '%Y-%m-%d').date() - hoje).days
        dias_restantes.append(dias)

    return jsonify({
        "objetivos": nomes,
        "restantes": dias_restantes
    })
