# 💰 Sistema Financeiro Pessoal

Sistema de controle financeiro pessoal via terminal (CLI), desenvolvido em Python com persistência de dados em PostgreSQL.

## 📋 Funcionalidades

- ✅ Cadastro de receitas e despesas
- ✅ Categorização de transações
- ✅ Resumo financeiro mensal (receitas, despesas e saldo)
- ✅ Geração de gráfico de despesas por categoria
- ✅ Cadastro e acompanhamento de metas financeiras

## 🛠️ Tecnologias utilizadas

- **Python**
- **SQLAlchemy** — ORM para modelagem e persistência dos dados
- **PostgreSQL** — banco de dados relacional
- **python-dotenv** — gerenciamento seguro de variáveis de ambiente
- **Matplotlib** — geração de gráficos
- **Tabulate** — formatação de tabelas no terminal

## 📁 Estrutura do projeto

```
financeiro_pessoal/
├── main.py
├── database.py
├── models.py
├── services/
│   ├── categoria_service.py
│   ├── transacao_service.py
│   └── meta_service.py
├── relatorios/
│   └── graficos.py
├── requirements.txt
└── .env (não versionado)
```

## 🚀 Como executar

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/financeiro-pessoal.git
cd financeiro-pessoal
```

### 2. Crie e ative um ambiente virtual (opcional, mas recomendado)
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Crie o banco de dados no PostgreSQL
```bash
psql -U postgres -c "CREATE DATABASE financeiro;"
```

### 5. Configure as variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto:
```
DATABASE_URL=postgresql://postgres:sua_senha@localhost:5432/financeiro
```

### 6. Execute o sistema
```bash
python main.py
```

## 🖥️ Menu do sistema

```
=== SISTEMA FINANCEIRO PESSOAL ===
1. Nova transação
2. Listar transações
3. Nova categoria
4. Resumo mensal
5. Gráfico de despesas por categoria
6. Nova meta
7. Listar metas
0. Sair
```

## 🔒 Segurança

As credenciais do banco de dados são carregadas via variáveis de ambiente (`.env`), que não é versionado no Git, evitando exposição de dados sensíveis no repositório.

