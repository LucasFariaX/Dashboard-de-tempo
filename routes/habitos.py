from flask import Blueprint, render_template, request, redirect, session
from database import get_db_connection
from datetime import datetime, date, timedelta

habitos_bp = Blueprint('habitos', __name__)

@habitos_bp.route('/habitos', methods=['GET', 'POST'])
def habitos():
    if 'usuario_id' not in session:
        return redirect('/login')

    conn = get_db_connection()

    if request.method == 'POST':
        nome = request.form['nome']
        meta = int(request.form.get('meta', 7))
        data = datetime.today().strftime('%Y-%m-%d')
        data_inicio = request.form.get('data_inicio')
        data_fim = request.form.get('data_fim')

        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO habitos (nome, data, concluido, data_inicio, data_fim)
            VALUES (?, ?, ?, ?, ?)
        ''', (nome, data, 0, data_inicio, data_fim))
        habito_id = cursor.lastrowid

        dias_semana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        # ✅ Adicionar como recorrente por padrão
        for dia in dias_semana:
            cursor.execute(
                'INSERT INTO habito_dias (habito_id, dia, feito, recorrente) VALUES (?, ?, ?, ?)',
                (habito_id, dia, 0, 1)
            )

        cursor.execute('INSERT INTO metas (habito_id, total_dias) VALUES (?, ?)', (habito_id, meta))
        conn.commit()

    filtro = request.args.get('filtro', 'todos')
    hoje = date.today()
    semana_atual = hoje.isocalendar()[1]
    mes_atual = hoje.month
    ano_atual = hoje.year

    habitos_raw = conn.execute('SELECT * FROM habitos').fetchall()
    habitos = []

    for h in habitos_raw:
        # Verificação segura de datas
        if "data_inicio" in h and h["data_inicio"]:
            if hoje < datetime.strptime(h["data_inicio"], "%Y-%m-%d").date():
                continue
        if "data_fim" in h and h["data_fim"]:
            if hoje > datetime.strptime(h["data_fim"], "%Y-%m-%d").date():
                continue

        dias_raw = conn.execute('SELECT * FROM habito_dias WHERE habito_id = ?', (h['id'],)).fetchall()
        dias_dict = {d['dia']: d['feito'] for d in dias_raw}
        recorrente_dict = {d['dia']: d['recorrente'] for d in dias_raw}

        feitos_na_semana = False
        feitos_no_mes = False
        feitos_total = 0

        for d in dias_raw:
            if d['feito']:
                dia_semana = d['dia']
                data_check = datetime.strptime(h['data'], '%Y-%m-%d')
                data_check += timedelta(days=["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"].index(dia_semana))
                if data_check.isocalendar()[1] == semana_atual and data_check.year == ano_atual:
                    feitos_na_semana = True
                if data_check.month == mes_atual and data_check.year == ano_atual:
                    feitos_no_mes = True
                feitos_total += 1

        if filtro == 'semana' and not feitos_na_semana:
            continue
        if filtro == 'mes' and not feitos_no_mes:
            continue

        meta_row = conn.execute('SELECT total_dias FROM metas WHERE habito_id = ?', (h['id'],)).fetchone()
        meta = meta_row['total_dias'] if meta_row else 7
        porcentagem = int((feitos_total / meta) * 100) if meta else 0

        habitos.append({
            'id': h['id'],
            'nome': h['nome'],
            'dias': dias_dict,
            'recorrente': recorrente_dict,
            'porcentagem': porcentagem,
            'total_feitos': feitos_total,
            'meta': meta
        })

    conn.close()
    return render_template('habitos.html', habitos=habitos, filtro=filtro)

@habitos_bp.route('/habitos/delete/<int:id>', methods=['POST'])
def deletar_habito(id):
    if 'usuario_id' not in session:
        return redirect('/login')
    conn = get_db_connection()
    conn.execute('DELETE FROM metas WHERE habito_id = ?', (id,))
    conn.execute('DELETE FROM habito_dias WHERE habito_id = ?', (id,))
    conn.execute('DELETE FROM habitos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/habitos')

@habitos_bp.route('/habitos/update', methods=['POST'])
def atualizar_checkbox():
    if 'usuario_id' not in session:
        return redirect('/login')
    habito_id = request.form['habito_id']
    dia = request.form['dia']
    estado = 1 if request.form.get('feito') == 'on' else 0
    conn = get_db_connection()
    conn.execute('UPDATE habito_dias SET feito = ? WHERE habito_id = ? AND dia = ?', (estado, habito_id, dia))
    conn.commit()
    conn.close()
    return redirect('/habitos')

@habitos_bp.route('/habitos/recorrencia', methods=['POST'])
def atualizar_recorrencia():
    if 'usuario_id' not in session:
        return redirect('/login')
    habito_id = request.form['habito_id']
    dia = request.form['dia']
    estado = 1 if request.form.get('recorrente') == 'on' else 0
    conn = get_db_connection()
    conn.execute('UPDATE habito_dias SET recorrente = ? WHERE habito_id = ? AND dia = ?', (estado, habito_id, dia))
    conn.commit()
    conn.close()
    return redirect('/habitos')
