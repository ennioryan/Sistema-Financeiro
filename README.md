# 💰 Sistema Financeiro Pessoal

Sistema de controle financeiro pessoal multiusuário, com backend em **FastAPI** e interface web moderna em **Dark Mode / Glassmorphism**, permitindo o registro de receitas, despesas, categorias e metas de economia, com visualização de resumos mensais e gráficos.

Este projeto nasceu como uma aplicação **CLI (linha de comando)** e evoluiu para uma **aplicação web completa e segura**, com autenticação JWT, cookies HttpOnly, isolamento de dados por usuário e validações rigorosas.

---

## ✨ Funcionalidades

- **Autenticação e Controle de Sessão**:
  - Cadastro de usuários com validação de regras de senha em tempo real
  - Criação automática de 6 categorias padrão na criação de conta
  - Login seguro com mensagens genéricas contra enumeração de credenciais
  - Autenticação via JSON Web Tokens (JWT) armazenados em cookies HttpOnly
  - Isolamento estrito de dados (cada usuário só visualiza, cria, edita e deleta seus próprios registros)
- **Lançamentos financeiros**: cadastro de receitas e despesas com descrição, valor, categoria e data
- **Edição e exclusão** de transações, com recálculo automático dos totais
- **Categorias personalizadas**: organização e agrupamento de receitas e despesas
- **Resumo mensal**: cards de Receitas, Despesas e Saldo Mensal, filtráveis por mês e ano
- **Gráficos interativos**: despesas por categoria em formato donut (Chart.js)
- **Metas de Economia**: acompanhamento visual de metas com valor alvo, prazo e progresso
- **Feedback visual premium**: skeletons/spinners de carregamento, checklist interativa de senha e notificações toast

---

## 🔐 Autenticação e Segurança

- **Senhas com Hash Seguro**: senhas são armazenadas com hash `bcrypt` e salt individual gerado automaticamente. O texto plano ou hash nunca aparecem em logs ou respostas da API.
- **Regras de Senha**:
  - Entre 6 e 14 caracteres
  - Pelo menos 1 letra maiúscula
  - Pelo menos 1 letra minúscula
  - Pelo menos 1 número
  - Pelo menos 1 caractere especial (`!@#$%^&*`, etc.)
- **Cookies HttpOnly**: tokens JWT transmitidos com flags `HttpOnly`, `SameSite=Lax` e suporte a `Secure` em produção, mitigando ataques de XSS e CSRF.
- **Proteção de Rotas**: dependência `get_current_user` valida assinatura e expiração do token em todas as chamadas da API (`/api/transacoes`, `/api/categorias`, `/api/metas`). Chamadas não autorizadas ou com sessão expirada redirecionam automaticamente para `/login`.

---

## 🛠️ Tecnologias

- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pydantic v2, PyJWT, Bcrypt
- **Banco de dados**: PostgreSQL, SQLAlchemy 2.0 (ORM)
- **Frontend**: HTML5, CSS3 Vanilla (Dark Mode / Glassmorphism, Google Fonts *Inter* & *Outfit*), JavaScript nativo (Fetch API), Chart.js, FontAwesome
- **CLI original**: Tabulate, Matplotlib

---

## 📁 Estrutura do projeto

```
├── main.py                     # Ponto de entrada da API (FastAPI, exception handlers, middlewares)
├── database.py                 # Conexão com PostgreSQL via SQLAlchemy
├── models.py                   # Modelos ORM (Usuario, Categoria, Transacao, Meta)
├── dependencies.py             # Dependências de injeção FastAPI (get_current_user)
├── schemas/                    # Schemas Pydantic para validação e serialização
│   ├── usuario.py
│   ├── categoria.py
│   ├── transacao.py
│   └── meta.py
├── routers/                    # Endpoints e rotas da API
│   ├── auth_router.py          # Autenticação (/cadastro, /login, /logout, /me)
│   ├── categoria_router.py     # CRUD de categorias
│   ├── transacao_router.py     # CRUD e resumos de transações
│   ├── meta_router.py          # Metas financeiras e progresso
│   └── views_router.py         # Renderização de views HTML (/, /login, /cadastro)
├── services/                    # Regras de negócio e operações no banco
│   ├── auth_service.py         # Hashing bcrypt, tokens JWT e cookies
│   ├── categoria_service.py    # Lógica de categorias isolada por usuario_id
│   ├── transacao_service.py    # Lógica de transações isolada por usuario_id
│   └── meta_service.py         # Lógica de metas isolada por usuario_id
├── templates/
│   ├── index.html              # Dashboard financeiro
│   ├── login.html              # Tela de login com card glassmorphism
│   └── cadastro.html           # Tela de cadastro com checklist de regras de senha
├── static/
│   ├── css/style.css           # Estilos globais Dark Mode / Glassmorphism
│   └── js/app.js               # Integração frontend com API, gráficos e interceptors
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## ⚙️ Instalação e Configuração

### Pré-requisitos
- Python 3.10 ou superior
- PostgreSQL instalado e em execução
- Gerenciador de pacotes pip

### 1. Clone o repositório
```bash
git clone https://github.com/ennioryan/Sistema-Financeiro.git
cd Sistema-Financeiro
```

### 2. Crie e ative um ambiente virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto baseado no `.env.example`:

```env
DATABASE_URL=postgresql://seu_usuario:sua_senha@localhost:5432/seu_banco_financeiro
SECRET_KEY=sua_chave_secreta_super_segura_aqui_gerada_aleatoriamente
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
COOKIE_SECURE=false
```

> **Dica**: Você pode gerar uma chave segura aleatória para a `SECRET_KEY` executando:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

---

## ▶️ Como executar a aplicação

Inicie o servidor de desenvolvimento com o Uvicorn:

```bash
uvicorn main:app --reload
```

Acesse em seu navegador:
```
http://localhost:8000
```

- Se não estiver autenticado, você será redirecionado para `http://localhost:8000/login`.
- A documentação interativa Swagger da API fica disponível em `http://localhost:8000/docs`.
