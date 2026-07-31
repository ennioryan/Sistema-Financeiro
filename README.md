# 💰 Sistema Financeiro Pessoal

Sistema de controle financeiro pessoal, com backend em **FastAPI** e interface web interativa, permitindo o registro de receitas, despesas, categorias e metas de economia, com visualização de resumos mensais e gráficos.

Este projeto nasceu como uma aplicação **CLI (linha de comando)** e evoluiu para uma **aplicação web completa**, mantendo a mesma camada de regras de negócio (services) por trás de ambas as interfaces.

---

## ✨ Funcionalidades

- **Lançamentos financeiros**: cadastro de receitas e despesas, com descrição, valor, categoria e data
- **Edição e exclusão** de transações, com recálculo automático dos totais
- **Categorias**: cadastro e organização de transações por categoria
- **Resumo mensal**: cards de Receitas, Despesas e Saldo Mensal, filtráveis por mês/ano
- **Gráfico de Despesas por Categoria** (visualização em donut chart)
- **Metas de Economia**: cadastro de metas com valor alvo, prazo e progresso visual
- **Estados de carregamento e erro**: skeletons/spinners durante requisições e mensagens de erro amigáveis em caso de falha

---

## 🛠️ Tecnologias

- **Backend**: Python, FastAPI, Uvicorn, Pydantic
- **Banco de dados**: PostgreSQL, SQLAlchemy (ORM)
- **Frontend**: HTML, CSS (Dark Mode / Glassmorphism), JavaScript (fetch API), Chart.js
- **CLI original**: Tabulate, Matplotlib

---

## 📁 Estrutura do projeto

```
├── main.py                     # Ponto de entrada da API (FastAPI, exception handlers, rotas)
├── database.py                 # Configuração da conexão com PostgreSQL
├── models.py                   # Modelos SQLAlchemy (Categoria, Transacao, Meta)
├── schemas/                    # Schemas Pydantic (validação de entrada/saída da API)
│   ├── categoria.py
│   ├── transacao.py
│   └── meta.py
├── routers/                    # Rotas da API organizadas por recurso
│   ├── categoria_router.py
│   ├── transacao_router.py
│   ├── meta_router.py
│   └── views_router.py         # Serve o dashboard (template principal)
├── services/                    # Regras de negócio (consumidas pelos routers)
│   ├── categoria_service.py
│   ├── transacao_service.py
│   └── meta_service.py
├── relatorios/
│   └── graficos.py              # Geração de gráficos (usado na versão original em CLI)
├── templates/
│   └── index.html                 # Template Jinja2 do dashboard
├── static/
│   ├── css/style.css               # Estilos (Dark Mode / Glassmorphism)
│   └── js/app.js                   # Lógica de integração com a API (fetch + Chart.js)
├── requirements.txt
└── .gitignore
```

---

## ⚙️ Instalação

### Pré-requisitos
- Python 3.10+
- PostgreSQL instalado e rodando localmente
- pip

### 1. Clone o repositório
```bash
git clone https://github.com/ennioryan/Sistema-Financeiro.git
cd Sistema-Financeiro
```

### 2. Crie e ative um ambiente virtual (recomendado)
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados
Crie um arquivo `.env` na raiz do projeto com suas credenciais do PostgreSQL:

```env
DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_do_banco
```

> Certifique-se de que o banco já foi criado no PostgreSQL (via pgAdmin ou terminal) antes de rodar a aplicação.

---

## ▶️ Como rodar

```bash
uvicorn main:app --reload
```
Depois, acesse no navegador:
```
http://localhost:8000
```

> **Nota**: a versão original do projeto era um sistema de linha de comando (CLI) com menu interativo via `input()`/`print()`. O `main.py` foi migrado integralmente para servir a API e o dashboard web; a lógica de negócio (`services/`) permanece a mesma que era usada pela versão CLI.

