🧠 Planner A1


🔎 Visão Geral

O *Planner A1* é um sistema pessoal de planejamento, desenvolvido com *Flask + SQLite + IndexedDB*, que simula um painel estilo Google Agenda + Notion para gerenciar:

* Hábitos com metas e rastreamento
* Compromissos com calendário interativo
* Objetivos com tarefas e consistência
* Anotações rápidas com suporte offline
* Dashboard com gráficos e heatmap
* Modo Foco com Pomodoro e progresso visual



🧰 Tecnologias Utilizadas

- Backend: Flask, SQLite3, Blueprints, Werkzeug.
- Frontend: HTML5, CSS3, JavaScript (Vanilla).
- Gráficos & Calendário: Chart.js, FullCalendar.
- Persistência Offline: IndexedDB (via JS).
- Visual responsivo: layout adaptado para mobile.


📂 Estrutura do Projeto

planner-a1/

├── app.py                  # Arquivo principal Flask
├── database.py             # Conexão com SQLite
├── routes/                 # Blueprints (agenda, habitos, dashboard, etc)
├── static/
    ├── css/                # Estilos por página
    └── js/                 # IndexedDB, Pomodoro
├── templates/              # HTMLs (Jinja2)
├── rotina.db               # Banco de dados SQLite



Funcionalidades

✅ Hábitos Inteligentes

* Criação de hábitos com datas de início/fim
* Definição de dias recorrentes (ex: Seg, Qua, Sex)
* Controle de checkboxes por dia da semana
* Cálculo de porcentagem de conclusão com meta definida
* Interface responsiva com botão colapsável para editar recorrência

🗓️ Agenda com Integração

* Calendário FullCalendar responsivo
* Eventos manuais e automáticos (baseados em hábitos recorrentes)
* Adição, edição e remoção de eventos
* Compromissos do dia atual e do dia seguinte em destaque

🎯 Objetivos com Tarefas

* Criação de objetivos com data final
* Registro de progresso diário (com consistência nos últimos 30 dias)
* Tarefas vinculadas a cada objetivo (com check)
* Conclusão de objetivo com data marcada
* Gráfico de consistência do objetivo (Chart.js)

📋 Anotações (Offline/Online)

* Anotações com textarea editável e salva automática
* Suporte a funcionamento **offline via IndexedDB**
* Sincroniza com backend ao reconectar

### 📊 Dashboard Visual

* Cards informativos (pendências, próximo evento, última nota)
* Gráfico de progresso semanal (Chart.js)
* Heatmap de hábitos (180 dias)
* Mini calendário de eventos
* Central analítica com percentual de cada módulo

🐺 Modo Foco ("Modo Caverna")

* Temporizador Pomodoro ajustável
* Exibição apenas do essencial: tarefas do dia, compromissos e progresso
* Suporte a anotações locais (via localStorage)

🔐 Sistema de Usuários

* Registro e login com senha criptografada (hash)
* Perfil com alteração de senha


📌 Status

> Projeto *100% funcional e pronto para uso local ou hospedagem em servidor Flask/Python.**


Criado por Lucas Faria
