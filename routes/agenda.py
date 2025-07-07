from flask import Blueprint, render_template, request, redirect, session, jsonify
from database import get_db_connection
from datetime import datetime, timedelta, date

agenda_bp = Blueprint('agenda', __name__)

@agenda_bp.route('/agenda', methods=['GET', 'POST'])
def agenda():
    if 'usuario_id' not in session:
        return redirect('/login')

    conn = get_db_connection()

    if request.method == 'POST':
        titulo = request.form['titulo']
        data = request.form['data']
        hora = request.form['hora']
        conn.execute('INSERT INTO agenda (titulo, data, hora) VALUES (?, ?, ?)', (titulo, data, hora))
        conn.commit()

    eventos = conn.execute('SELECT * FROM agenda ORDER BY data, hora').fetchall()

    hoje = datetime.today().strftime('%Y-%m-%d')
    amanha = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')

    eventos_hoje = conn.execute("SELECT titulo, hora FROM agenda WHERE data = ? ORDER BY hora", (hoje,)).fetchall()
    eventos_amanha = conn.execute("SELECT titulo, hora FROM agenda WHERE data = ? ORDER BY hora", (amanha,)).fetchall()

    conn.close()

    return render_template(
        'agenda.html',
        eventos=eventos,
        eventos_hoje=eventos_hoje,
        eventos_amanha=eventos_amanha
    )


@agenda_bp.route('/eventos', methods=['GET', 'POST'])
def eventos():
    if 'usuario_id' not in session:
        return redirect('/login')

    conn = get_db_connection()

    if request.method == 'GET':
        eventos = conn.execute('SELECT id, titulo, data, hora FROM agenda').fetchall()

        # Buscar hábitos recorrentes dentro do intervalo data_inicio - data_fim
        habitos = conn.execute('''
            SELECT h.id, h.nome, h.data_inicio, h.data_fim, d.dia
            FROM habitos h
            JOIN habito_dias d ON h.id = d.habito_id
            WHERE d.recorrente = 1
        ''').fetchall()

        hoje = datetime.today()
        eventos_habitos = []
        dias_semana = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

        for i in range(0, 30):  # Próximos 30 dias
            data_iter = hoje + timedelta(days=i)
            dia_nome = dias_semana[data_iter.weekday()]
            data_str = data_iter.strftime('%Y-%m-%d')

            for h in habitos:
                # Validar se data está dentro do intervalo
                if h["data_inicio"] and data_str < h["data_inicio"]:
                    continue
                if h["data_fim"] and data_str > h["data_fim"]:
                    continue

                if h["dia"] == dia_nome:
                    eventos_habitos.append({
                        "id": f"habito-{h['id']}-{i}",
                        "title": h["nome"],
                        "start": f"{data_str}T08:00"
                    })

        eventos_agenda = [
            {
                "id": e["id"],
                "title": e["titulo"],
                "start": f"{e['data']}T{e['hora']}"
            } for e in eventos
        ]

        conn.close()
        return jsonify(eventos_agenda + eventos_habitos)

    if request.method == 'POST':
        data = request.json.get('data')
        hora = request.json.get('hora')
        titulo = request.json.get('titulo')
        conn.execute('INSERT INTO agenda (titulo, data, hora) VALUES (?, ?, ?)', (titulo, data, hora))
        conn.commit()
        conn.close()
        return jsonify({'status': 'ok'})


@agenda_bp.route('/eventos/delete', methods=['POST'])
def deletar_evento():
    if 'usuario_id' not in session:
        return redirect('/login')
    id = request.json.get('id')
    conn = get_db_connection()
    conn.execute('DELETE FROM agenda WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'deleted'})
