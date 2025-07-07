import sqlite3

# Conexão reutilizável para todos os módulos
def get_db_connection():
    conn = sqlite3.connect('rotina.db')
    conn.row_factory = sqlite3.Row
    return conn

# Inicialização do banco com todas as tabelas do sistema
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    ''')

    # Tabela de hábitos com datas de início e fim
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habitos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            data TEXT NOT NULL,
            concluido INTEGER DEFAULT 0,
            data_inicio TEXT,
            data_fim TEXT
        )
    ''')

    # Tabela de dias dos hábitos com recorrência
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habito_dias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habito_id INTEGER NOT NULL,
            dia TEXT NOT NULL,
            feito INTEGER DEFAULT 0,
            recorrente INTEGER DEFAULT 1,
            FOREIGN KEY (habito_id) REFERENCES habitos(id)
        )
    ''')

    # Tabela de marcações reais de hábitos por data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habito_registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habito_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            feito INTEGER DEFAULT 1,
            FOREIGN KEY (habito_id) REFERENCES habitos(id)
        )
    ''')

    # Tabela de metas por hábito
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habito_id INTEGER NOT NULL,
            total_dias INTEGER NOT NULL,
            FOREIGN KEY (habito_id) REFERENCES habitos(id)
        )
    ''')

    # Tabela de compromissos da agenda
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agenda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            data TEXT NOT NULL,
            hora TEXT NOT NULL
        )
    ''')

    # Tabela de anotações
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS anotacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conteudo TEXT NOT NULL,
            data TEXT NOT NULL
        )
    ''')

    # Tabela de objetivos com data final e conclusão
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS objetivos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            data_final TEXT NOT NULL,
            data_conclusao TEXT DEFAULT NULL
        )
    ''')

    # Tabela de tarefas por objetivo
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            objetivo_id INTEGER NOT NULL,
            descricao TEXT NOT NULL,
            concluida INTEGER DEFAULT 0,
            FOREIGN KEY (objetivo_id) REFERENCES objetivos(id)
        )
    ''')

    # Tabela de marcações de progresso diário dos objetivos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS objetivo_marcacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            objetivo_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            observacao TEXT,
            FOREIGN KEY (objetivo_id) REFERENCES objetivos(id)
        )
    ''')



    conn.commit()
    conn.close()

# Utilitário para ativar recorrência manual
def ativar_recorrencia(habito_id, dia):
    conn = get_db_connection()
    conn.execute("UPDATE habito_dias SET recorrente = 1 WHERE habito_id = ? AND dia = ?", (habito_id, dia))
    conn.commit()
    conn.close()
    print(f"Hábito {habito_id} ativado como recorrente para o dia {dia}.")

# Execução direta para criar o banco ou testar ações
if __name__ == '__main__':
    # init_db()  # Descomente para rodar e criar as tabelas
    ativar_recorrencia(1, 'Qui')  # Exemplo de ativação para quinta-feira


