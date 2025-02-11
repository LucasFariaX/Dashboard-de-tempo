import sqlite3

# Conectar ao banco de dados
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Criar tabela de objetivos (caso não exista)
cursor.execute('''
CREATE TABLE IF NOT EXISTS objetivos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    meta INTEGER NOT NULL,
    progresso INTEGER DEFAULT 0
)
''')

# Criar tabela de pontos (para entrada/saída)
cursor.execute('''
CREATE TABLE IF NOT EXISTS pontos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    objetivo_id INTEGER NOT NULL,
    entrada TEXT NOT NULL,
    saida TEXT,
    FOREIGN KEY (objetivo_id) REFERENCES objetivos (id)
)
''')

# Criar nova tabela de tarefas (to-do list)
cursor.execute('''
CREATE TABLE IF NOT EXISTS tarefas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    objetivo_id INTEGER NOT NULL,
    descricao TEXT NOT NULL,
    concluida INTEGER DEFAULT 0,
    FOREIGN KEY (objetivo_id) REFERENCES objetivos (id)
)
''')

# Salvar mudanças e fechar conexão
conn.commit()
conn.close()

print("Banco de dados atualizado com sucesso!")


if __name__ == "__main__":
    criar_banco()
