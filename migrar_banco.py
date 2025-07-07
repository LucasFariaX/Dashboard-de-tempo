import sqlite3

def coluna_existe(cursor, tabela, coluna):
    cursor.execute(f"PRAGMA table_info({tabela})")
    colunas = [col[1] for col in cursor.fetchall()]
    return coluna in colunas

def migrar():
    conn = sqlite3.connect('rotina.db')
    cursor = conn.cursor()

    if not coluna_existe(cursor, "habitos", "data_inicio"):
        print("Adicionando coluna 'data_inicio'...")
        cursor.execute("ALTER TABLE habitos ADD COLUMN data_inicio TEXT")

    if not coluna_existe(cursor, "habitos", "data_fim"):
        print("Adicionando coluna 'data_fim'...")
        cursor.execute("ALTER TABLE habitos ADD COLUMN data_fim TEXT")

    conn.commit()
    conn.close()
    print("✅ Migração concluída com sucesso.")

if __name__ == "__main__":
    migrar()
