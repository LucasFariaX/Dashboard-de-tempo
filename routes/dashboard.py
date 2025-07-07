# dashboard.py atualizado

from flask import Blueprint, render_template, session, redirect
import sqlite3
from datetime import datetime, date, timedelta

# Blueprint da dashboard
dashboard_bp = Blueprint('dashboard', __name__)

# Função de conexão com o banco de dados

def get_db_connection():
    conn = sqlite3.connect('rotina.db')
    conn.row_factory = sqlite3.Row
    return conn

# Rota padrão da dashboard
@dashboard_bp.route('/')
def home():
    if 'usuario_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    hoje = date.today()
    dia_semana_str = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"][hoje.weekday()]

    # Hábitos pendentes do dia
    pendentes = conn.execute("""
        SELECT COUNT(*) AS total
        FROM habito_dias hd
        JOIN habitos h ON h.id = hd.habito_id
        WHERE hd.dia = ? AND hd.feito = 0
    """, (dia_semana_str,)).fetchone()["total"]

    # Próximo compromisso
    proximo_evento = conn.execute("""
        SELECT titulo, data, hora
        FROM agenda
        WHERE datetime(data || ' ' || hora) >= datetime('now')
        ORDER BY data ASC, hora ASC
        LIMIT 1
    """).fetchone()
    compromisso = f"{proximo_evento['titulo']} - {proximo_evento['hora']}" if proximo_evento else "Nenhum evento futuro"

    # Última anotação
    ultima_nota = conn.execute("SELECT conteudo FROM anotacoes ORDER BY id DESC LIMIT 1").fetchone()
    nota = ultima_nota["conteudo"] if ultima_nota else "Nenhuma anotação encontrada"

    # Objetivos
    objetivos_raw = conn.execute("SELECT nome, data_final, data_conclusao FROM objetivos").fetchall()
    objetivos = []
    for obj in objetivos_raw:
        dias_restantes = (datetime.strptime(obj["data_final"], "%Y-%m-%d").date() - hoje).days
        objetivos.append({
            "nome": obj["nome"],
            "dias_restantes": dias_restantes,
            "concluido": obj["data_conclusao"] is not None,
            "data_conclusao": obj["data_conclusao"]
        })

    # Gráfico de hábitos dos últimos 7 dias
    habitos_7dias = []
    for i in range(6, -1, -1):
        data_check = hoje - timedelta(days=i)
        dia_semana = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"][data_check.weekday()]
        count = conn.execute("""
            SELECT COUNT(*) FROM habito_dias
            WHERE dia = ? AND feito = 1
        """, (dia_semana,)).fetchone()[0]
        habitos_7dias.append({"dia": dia_semana, "quantidade": count})

    # Lista de hábitos com progresso
    habitos_raw = conn.execute("SELECT * FROM habitos").fetchall()
    habitos_ativos = []
    dias_heatmap = []
    for h in habitos_raw:
        dias_raw = conn.execute("SELECT * FROM habito_dias WHERE habito_id = ?", (h["id"],)).fetchall()
        feitos_total = sum(1 for d in dias_raw if d["feito"])
        meta_row = conn.execute("SELECT total_dias FROM metas WHERE habito_id = ?", (h["id"],)).fetchone()
        meta = meta_row["total_dias"] if meta_row else 7
        porcentagem = int((feitos_total / meta) * 100) if meta else 0
        habitos_ativos.append({
            "nome": h["nome"],
            "porcentagem": porcentagem
        })

    # Heatmap 180 dias
    for i in range(180):
        dia = hoje - timedelta(days=179 - i)
        dia_str = dia.strftime('%Y-%m-%d')
        dia_semana = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"][dia.weekday()]
        count = conn.execute("SELECT COUNT(*) FROM habito_dias WHERE dia = ? AND feito = 1", (dia_semana,)).fetchone()[0]
        if count == 0:
            nivel = 0
        elif count < 2:
            nivel = 1
        elif count < 4:
            nivel = 2
        elif count < 6:
            nivel = 3
        else:
            nivel = 4
        dias_heatmap.append({"data": dia_str, "nivel": nivel})

    total_habitos = conn.execute("SELECT COUNT(*) FROM habito_dias WHERE feito = 1 AND strftime('%W', 'now') = strftime('%W', 'now')").fetchone()[0]
    total_eventos = conn.execute("SELECT COUNT(*) FROM agenda WHERE strftime('%W', data) = strftime('%W', 'now')").fetchone()[0]
    total_anotacoes = conn.execute("SELECT COUNT(*) FROM anotacoes WHERE strftime('%W', data) = strftime('%W', 'now')").fetchone()[0]
    total_objetivos = len(objetivos)

    conn.close()

    return render_template(
        'home.html',
        pendentes=pendentes,
        compromisso=compromisso,
        nota=nota,
        objetivos=objetivos,
        habitos_7dias=habitos_7dias,
        habitos_ativos=habitos_ativos,
        habitos_heatmap=dias_heatmap,
        grafico_data={
            'habitos': total_habitos,
            'agenda': total_eventos,
            'anotacoes': total_anotacoes,
            'objetivos': total_objetivos
        }
    )

# Rota do modo foco
@dashboard_bp.route('/modo_foco')
def modo_foco():
    if 'usuario_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    hoje = date.today().strftime('%Y-%m-%d')

    # Tarefas do dia
    tarefas = conn.execute("""
        SELECT t.id, t.descricao, t.concluida
        FROM tarefas t
        JOIN objetivos o ON o.id = t.objetivo_id
        WHERE o.data_final >= ?
    """, (hoje,)).fetchall()


    # Compromissos do dia
    eventos_hoje = conn.execute("""
        SELECT titulo, hora FROM agenda
        WHERE data = ?
        ORDER BY hora ASC
    """, (hoje,)).fetchall()


    # Progresso simples
    total_habitos = conn.execute("SELECT COUNT(*) FROM habito_dias").fetchone()[0]
    feitos_habitos = conn.execute("SELECT COUNT(*) FROM habito_dias WHERE feito = 1").fetchone()[0]

    total_tarefas = conn.execute("SELECT COUNT(*) FROM tarefas").fetchone()[0]
    feitas_tarefas = conn.execute("SELECT COUNT(*) FROM tarefas WHERE concluida = 1").fetchone()[0]

    conn.close()

    progresso = {
        'habitos': int((feitos_habitos / total_habitos) * 100) if total_habitos else 0,
        'tarefas': int((feitas_tarefas / total_tarefas) * 100) if total_tarefas else 0,
    }
    progresso['total'] = int((progresso['habitos'] + progresso['tarefas']) / 2)

    return render_template('modo_foco.html', tarefas_dia=tarefas, eventos_hoje=eventos_hoje, progresso=progresso)


@dashboard_bp.route('/modo_foco/tarefa/concluir/<int:tarefa_id>', methods=['POST'])
def concluir_tarefa_foco(tarefa_id):
    if 'usuario_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    conn.execute("UPDATE tarefas SET concluida = 1 WHERE id = ?", (tarefa_id,))
    conn.commit()
    conn.close()

    return redirect('/modo_foco')


