Rastreador de Objetivos

Este projeto é um rastreador de objetivos que permite registrar e acompanhar o progresso de metas pessoais, registrando tempo investido e tarefas concluídas. Ele utiliza Flask para o backend e SQLite para armazenamento de dados.

Funcionalidades
- Criar, editar e excluir objetivos.
- Registrar entradas e saídas para acompanhar o tempo investido.
- Adicionar, concluir e excluir tarefas relacionadas a um objetivo.
- Exibir o progresso em gráficos dinâmicos.

Tecnologias Utilizadas
- Backend: Python (Flask)
- Banco de Dados: SQLite
- Frontend: HTML, CSS
- Bibliotecas:
  - Flask
  - Chart.js (para gráficos)

📂 Estrutura do Projeto
```
📁 projeto
│-- 📄 app.py              # Backend Flask
│-- 📄 database.db         # Banco de dados SQLite
│-- 📄 index.html          # Página principal
│-- 📄 editar_objetivo.html # Página para editar objetivos
│-- 📄 registros.html      # Página de registros de tempo
│-- 📁 static
│   ├── 📄 styles.css      # Estilos da aplicação
│-- 📁 templates
│   ├── 📄 index.html      # Interface principal
│   ├── 📄 editar_objetivo.html # Edição de objetivos
│   ├── 📄 registros.html  # Histórico de registros
```

Como Executar
1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/projeto-rastreador.git
cd projeto-rastreador
```

2. Crie e ative um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows
```

3. Instale as dependências
```bash
pip install flask
```

4. Crie o banco de dados
```bash
python
>>> import sqlite3
>>> conn = sqlite3.connect('database.db')
>>> conn.execute('''CREATE TABLE IF NOT EXISTS objetivos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        meta INTEGER NOT NULL,
        progresso INTEGER DEFAULT 0
    );''')
>>> conn.execute('''CREATE TABLE IF NOT EXISTS pontos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        objetivo_id INTEGER,
        entrada TEXT,
        saida TEXT,
        FOREIGN KEY (objetivo_id) REFERENCES objetivos(id)
    );''')
>>> conn.execute('''CREATE TABLE IF NOT EXISTS tarefas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        objetivo_id INTEGER,
        descricao TEXT,
        concluida INTEGER DEFAULT 0,
        FOREIGN KEY (objetivo_id) REFERENCES objetivos(id)
    );''')
>>> conn.commit()
>>> conn.close()
```

5. Inicie o servidor Flask
```bash
python app.py
```

6. Acesse a aplicação no navegador
```
http://127.0.0.1:5000/
```

 Como Contribuir
1. Faça um fork do projeto.
2. Crie uma branch (`git checkout -b minha-feature`).
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`).
4. Envie um push para a branch (`git push origin minha-feature`).
5. Abra um Pull Request.

---

Criado por Lucas Faria [(https://github.com/seu-usuario)](https://github.com/LucasFariaX)

