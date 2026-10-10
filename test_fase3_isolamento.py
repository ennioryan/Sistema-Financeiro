import sys
import os
import json
import time
import threading
import urllib.request
import urllib.error
import http.cookiejar
from datetime import date

# Adicionar pasta atual ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_session
from models import Usuario, Categoria, Transacao, Meta
import uvicorn
from main import app

SERVER_PORT = 8011
BASE_URL = f"http://127.0.0.1:{SERVER_PORT}"

class ClientSession:
    """Cliente HTTP com suporte a cookies e cabeçalhos para simular navegador/sessão do usuário."""
    def __init__(self):
        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar)
        )

    def request(self, method, path, data=None, headers=None):
        url = f"{BASE_URL}{path}"
        req_headers = {"Accept": "application/json"}
        req_data = None
        if data is not None:
            req_data = json.dumps(data).encode("utf-8")
            req_headers["Content-Type"] = "application/json"
        if headers:
            req_headers.update(headers)

        req = urllib.request.Request(url, data=req_data, headers=req_headers, method=method)
        try:
            with self.opener.open(req) as resp:
                status_code = resp.status
                body = resp.read().decode("utf-8")
                cookie_headers = resp.headers.get_all("Set-Cookie") or []
                try:
                    json_body = json.loads(body) if body else None
                except Exception:
                    json_body = body
                return status_code, json_body, cookie_headers
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            cookie_headers = e.headers.get_all("Set-Cookie") or []
            try:
                json_body = json.loads(err_body) if err_body else None
            except Exception:
                json_body = err_body
            return e.code, json_body, cookie_headers

def run_tests():
    print("=" * 60)
    print("INICIANDO BATERIA DE TESTES AUTOMATIZADOS - FASE 3")
    print("=" * 60)

    # 1. Iniciar servidor uvicorn em background
    config = uvicorn.Config(app, host="127.0.0.1", port=SERVER_PORT, log_level="warning")
    server = uvicorn.Server(config)
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()
    time.sleep(1.2)

    # E-mails de teste únicos
    EMAIL_A = "usuario_a_teste_fase3@exemplo.com"
    EMAIL_B = "usuario_b_teste_fase3@exemplo.com"
    SENHA_A = "SenhaValida1!"
    SENHA_B = "SenhaValida2@"

    session_db = get_session()
    # Garantir que banco está limpo de execuções anteriores se houver
    try:
        users = session_db.query(Usuario).filter(Usuario.email.in_([EMAIL_A, EMAIL_B])).all()
        for u in users:
            session_db.delete(u)
        session_db.commit()
    finally:
        session_db.close()

    user_a_id = None
    user_b_id = None

    client_a = ClientSession()
    client_b = ClientSession()
    client_anon = ClientSession()

    try:
        # TESTE 1: Cadastro de Usuário A
        print("\n[1] Testando cadastro do Usuário A...")
        status, body, cookies = client_a.request("POST", "/api/auth/cadastro", {
            "nome": "Usuário Teste A",
            "email": EMAIL_A,
            "senha": SENHA_A
        })
        assert status == 201, f"Esperado 201, obtido {status}: {body}"
        assert "access_token" in body, "Token de acesso não retornado"
        assert "usuario" in body, "Objeto de usuário ausente"
        assert body["usuario"]["email"] == EMAIL_A
        assert "senha" not in body["usuario"] and "senha_hash" not in body["usuario"]
        assert any("access_token" in c for c in cookies), "Cookie access_token não foi definido no header Set-Cookie"
        user_a_id = body["usuario"]["id"]
        print(f"  -> Usuário A criado com sucesso! ID={user_a_id}")

        # TESTE 2: Validação de Senha em Hash no Banco
        print("\n[2] Validando que a senha do Usuário A está em hash bcrypt no banco...")
        session_db = get_session()
        try:
            u_db = session_db.query(Usuario).filter_by(id=user_a_id).first()
            assert u_db is not None
            assert u_db.senha_hash != SENHA_A, "Senha gravada em texto plano!"
            assert u_db.senha_hash.startswith("$2b$") or u_db.senha_hash.startswith("$2a$"), "Senha não usa hash bcrypt válido!"
            print("  -> Senha gravada com hash seguro bcrypt com salt.")
        finally:
            session_db.close()

        # TESTE 3: Bloqueio de E-mail Duplicado (409)
        print("\n[3] Testando bloqueio de e-mail duplicado (409)...")
        status, body, _ = client_anon.request("POST", "/api/auth/cadastro", {
            "nome": "Outro Usuário",
            "email": EMAIL_A,
            "senha": "OutraSenha123#"
        })
        assert status == 409, f"Esperado 409 para e-mail duplicado, obtido {status}: {body}"
        print("  -> E-mail duplicado bloqueado com status HTTP 409 com sucesso.")

        # TESTE 4: Cadastro de Usuário B
        print("\n[4] Testando cadastro do Usuário B...")
        status, body, cookies = client_b.request("POST", "/api/auth/cadastro", {
            "nome": "Usuário Teste B",
            "email": EMAIL_B,
            "senha": SENHA_B
        })
        assert status == 201, f"Esperado 201, obtido {status}: {body}"
        user_b_id = body["usuario"]["id"]
        assert user_b_id != user_a_id, "IDs dos usuários devem ser diferentes!"
        print(f"  -> Usuário B criado com sucesso! ID={user_b_id}")

        # TESTE 5: Criação das 6 Categorias Padrão
        print("\n[5] Validando categorias padrão de cada usuário...")
        status_cats_a, cats_a, _ = client_a.request("GET", "/api/categorias")
        assert status_cats_a == 200, f"Erro ao listar categorias de A: {cats_a}"
        status_cats_b, cats_b, _ = client_b.request("GET", "/api/categorias")
        assert status_cats_b == 200, f"Erro ao listar categorias de B: {cats_b}"

        nomes_esperados = {"Alimentação", "Transporte", "Moradia", "Lazer", "Salário", "Investimentos"}
        nomes_a = {c["nome"] for c in cats_a}
        nomes_b = {c["nome"] for c in cats_b}
        assert nomes_esperados.issubset(nomes_a), f"Usuário A não recebeu todas categorias padrão: {nomes_a}"
        assert nomes_esperados.issubset(nomes_b), f"Usuário B não recebeu todas categorias padrão: {nomes_b}"

        # Garantir que os IDs das categorias de A são distintos dos IDs de B
        ids_a = {c["id"] for c in cats_a}
        ids_b = {c["id"] for c in cats_b}
        assert ids_a.isdisjoint(ids_b), "Categorias de A e B compartilham IDs no banco!"
        print(f"  -> Ambos usuários receberam suas 6 categorias padrão com isolamento completo de IDs.")

        # TESTE 6: Teste de Login
        print("\n[6] Testando rotas de login...")
        # Senha errada
        status, body, _ = client_anon.request("POST", "/api/auth/login", {
            "email": EMAIL_A,
            "senha": "SenhaErrada123!"
        })
        assert status == 401, f"Esperado 401, obtido {status}"
        assert body["detail"] == "E-mail ou senha inválidos", f"Mensagem não é genérica: {body}"

        # Email errado
        status, body, _ = client_anon.request("POST", "/api/auth/login", {
            "email": "inexistente@teste.com",
            "senha": "QualquerCoisa1!"
        })
        assert status == 401, f"Esperado 401, obtido {status}"
        assert body["detail"] == "E-mail ou senha inválidos", f"Mensagem não é genérica: {body}"

        # Login correto
        status, body, cookies = client_anon.request("POST", "/api/auth/login", {
            "email": EMAIL_A,
            "senha": SENHA_A
        })
        assert status == 200, f"Esperado 200, obtido {status}"
        assert any("access_token" in c for c in cookies)
        print("  -> Login validado: mensagem de erro genérica em falhas e sucesso com cookie em acerto.")

        # TESTE 7: Endpoint GET /api/auth/me
        print("\n[7] Testando endpoint /api/auth/me...")
        status, me_a, _ = client_a.request("GET", "/api/auth/me")
        assert status == 200 and me_a["id"] == user_a_id and me_a["email"] == EMAIL_A
        assert "senha" not in me_a and "senha_hash" not in me_a

        status, me_b, _ = client_b.request("GET", "/api/auth/me")
        assert status == 200 and me_b["id"] == user_b_id and me_b["email"] == EMAIL_B
        assert "senha" not in me_b and "senha_hash" not in me_b

        # Sem autenticação
        status, _, _ = ClientSession().request("GET", "/api/auth/me")
        assert status == 401, f"Esperado 401 sem token, obtido {status}"
        print("  -> /api/auth/me retorna dados corretos isolados por sessão e bloqueia acessos anônimos.")

        # TESTE 8: Isolamento de Categorias (Criação de categoria própria)
        print("\n[8] Testando isolamento na criação e listagem de categorias...")
        status, cat_gamer_a, _ = client_a.request("POST", "/api/categorias", {
            "nome": "Games A",
            "tipo": "despesa"
        })
        assert status == 200, f"Erro ao criar categoria para A: {cat_gamer_a}"

        # B lista categorias e NÃO deve ver "Games A"
        status, cats_b_now, _ = client_b.request("GET", "/api/categorias")
        assert all(c["nome"] != "Games A" for c in cats_b_now), "Usuário B enxergou categoria do Usuário A!"
        print("  -> Categoria personalizada do Usuário A NÃO é visível para o Usuário B.")

        # TESTE 9: Criação de Transações e Isolamento de Leitura
        print("\n[9] Testando criação e isolamento de transações...")
        cat_alimentacao_a = next(c["id"] for c in cats_a if c["nome"] == "Alimentação")
        cat_salario_a = next(c["id"] for c in cats_a if c["nome"] == "Salário")
        cat_alimentacao_b = next(c["id"] for c in cats_b if c["nome"] == "Alimentação")

        # Usuário A cria 1 despesa e 1 receita
        status, tx_a1, _ = client_a.request("POST", "/api/transacoes", {
            "descricao": "Mercado A",
            "valor": 150.0,
            "tipo": "despesa",
            "categoria_id": cat_alimentacao_a,
            "data": str(date.today())
        })
        assert status == 200, f"Erro ao criar tx A1: {tx_a1}"

        status, tx_a2, _ = client_a.request("POST", "/api/transacoes", {
            "descricao": "Salário Mensal A",
            "valor": 5000.0,
            "tipo": "receita",
            "categoria_id": cat_salario_a,
            "data": str(date.today())
        })
        assert status == 200, f"Erro ao criar tx A2: {tx_a2}"

        # Usuário B cria 1 despesa
        status, tx_b1, _ = client_b.request("POST", "/api/transacoes", {
            "descricao": "Mercado B",
            "valor": 320.0,
            "tipo": "despesa",
            "categoria_id": cat_alimentacao_b,
            "data": str(date.today())
        })
        assert status == 200, f"Erro ao criar tx B1: {tx_b1}"

        # Listagem de A: deve conter apenas tx de A
        status, list_a, _ = client_a.request("GET", "/api/transacoes")
        assert len(list_a) == 2, f"Usuário A deveria ver 2 transações, viu {len(list_a)}"
        assert all(t["descricao"] != "Mercado B" for t in list_a), "Usuário A enxergou transação do Usuário B!"

        # Listagem de B: deve conter apenas tx de B
        status, list_b, _ = client_b.request("GET", "/api/transacoes")
        assert len(list_b) == 1, f"Usuário B deveria ver 1 transação, viu {len(list_b)}"
        assert list_b[0]["descricao"] == "Mercado B"
        print("  -> Listagem de transações perfeitamente isolada entre usuários.")

        # TESTE 10: Resumo Mensal Isolado
        print("\n[10] Testando isolamento no resumo mensal...")
        hoje = date.today()
        status, res_a, _ = client_a.request("GET", f"/api/transacoes/resumo?mes={hoje.month}&ano={hoje.year}")
        assert status == 200
        assert res_a["receitas"] == 5000.0
        assert res_a["despesas"] == 150.0
        assert res_a["saldo"] == 4850.0

        status, res_b, _ = client_b.request("GET", f"/api/transacoes/resumo?mes={hoje.month}&ano={hoje.year}")
        assert status == 200
        assert res_b["receitas"] == 0.0
        assert res_b["despesas"] == 320.0
        assert res_b["saldo"] == -320.0
        print("  -> Resumo financeiro mensal calcula apenas valores do próprio usuário.")

        # TESTE 11: Tentativas de Acesso Cruzado Proibido (Injeção de Categoria Alheia)
        print("\n[11] Testando bloqueio de uso de categoria de outro usuário...")
        # Usuário A tenta criar transação com categoria pertencente a B
        status, erro_cat_cruzada, _ = client_a.request("POST", "/api/transacoes", {
            "descricao": "Tentativa Invasiva",
            "valor": 100.0,
            "tipo": "despesa",
            "categoria_id": cat_alimentacao_b,
            "data": str(date.today())
        })
        assert status == 400, f"Esperado 400 ao usar categoria alheia, obtido {status}: {erro_cat_cruzada}"
        print("  -> Rejeitado com sucesso: usuário não pode vincular transações a categorias de terceiros.")

        # TESTE 12: Tentativa de Exclusão de Transação Alheia
        print("\n[12] Testando bloqueio de exclusão cruzada...")
        tx_b_id = tx_b1["id"]
        status, del_resp, _ = client_a.request("DELETE", f"/api/transacoes/{tx_b_id}")
        assert status == 404, f"Usuário A conseguiu interagir com transação de B! Status: {status}"

        # Verifica no banco que a transação de B ainda existe intacta
        session_db = get_session()
        try:
            tx_b_db = session_db.query(Transacao).filter_by(id=tx_b_id).first()
            assert tx_b_db is not None, "Transação de B foi excluída indevidamente!"
            print("  -> Exclusão proibida (HTTP 404) e registro mantido íntegro no banco.")
        finally:
            session_db.close()

        # TESTE 13: Tentativa de Edição de Transação Alheia
        print("\n[13] Testando bloqueio de edição cruzada...")
        status, edit_resp, _ = client_a.request("PUT", f"/api/transacoes/{tx_b_id}", {
            "descricao": "Tentativa Hacker",
            "valor": 9999.0,
            "tipo": "despesa",
            "categoria_id": cat_alimentacao_a
        })
        assert status == 404, f"Usuário A conseguiu editar transação de B! Status: {status}"

        # Verifica no banco que os dados de B não foram alterados
        session_db = get_session()
        try:
            tx_b_db = session_db.query(Transacao).filter_by(id=tx_b_id).first()
            assert tx_b_db.valor == 320.0, "Valor de transação alheia foi alterado!"
            print("  -> Edição proibida (HTTP 404) e dados de B inalterados.")
        finally:
            session_db.close()

        # TESTE 14: Isolamento de Metas
        print("\n[14] Testando isolamento no módulo de metas...")
        status, meta_a, _ = client_a.request("POST", "/api/metas", {
            "nome": "Reserva A",
            "valor_alvo": 10000.0,
            "prazo": str(date(2027, 12, 31))
        })
        assert status == 200, f"Erro ao criar meta de A: {meta_a}"
        meta_a_id = meta_a["id"]

        status, meta_b, _ = client_b.request("POST", "/api/metas", {
            "nome": "Carro B",
            "valor_alvo": 50000.0,
            "prazo": str(date(2028, 6, 30))
        })
        assert status == 200, f"Erro ao criar meta de B: {meta_b}"
        meta_b_id = meta_b["id"]

        # Listagem de A: vê apenas meta de A
        status, metas_a_list, _ = client_a.request("GET", "/api/metas")
        assert len(metas_a_list) == 1 and metas_a_list[0]["nome"] == "Reserva A"

        # Listagem de B: vê apenas meta de B
        status, metas_b_list, _ = client_b.request("GET", "/api/metas")
        assert len(metas_b_list) == 1 and metas_b_list[0]["nome"] == "Carro B"

        # Usuário A tenta atualizar progresso na meta de B
        status, patch_resp, _ = client_a.request("PATCH", f"/api/metas/{meta_b_id}/progresso", {
            "valor": 500.0
        })
        assert status == 404, f"Usuário A conseguiu atualizar meta de B! Status: {status}"

        # Verifica que progresso de B continua zerado
        session_db = get_session()
        try:
            m_b_db = session_db.query(Meta).filter_by(id=meta_b_id).first()
            assert m_b_db.valor_atual == 0.0, "Progresso da meta de B foi adulterado!"
            print("  -> Metas totalmente isoladas: listagem e atualizações protegidas.")
        finally:
            session_db.close()

        # TESTE 15: Logout
        print("\n[15] Testando rota de logout...")
        status, logout_body, cookies = client_a.request("POST", "/api/auth/logout")
        assert status == 200
        # Cookie deve ter sido removido (Max-Age=0 ou expires no passado)
        assert any("access_token=\"\"" in c or "Max-Age=0" in c or "expires=" in c.lower() for c in cookies)
        print("  -> Logout removeu o cookie de autenticação com sucesso.")

        # TESTE 16: Não vazamento de senhas em validações 422
        print("\n[16] Testando não-vazamento de senha em resposta de erro de validação (422)...")
        status, err_422, _ = client_anon.request("POST", "/api/auth/cadastro", {
            "nome": "Nome",
            "email": "teste422@teste.com",
            "senha": "123" # Senha inválida propositalmente
        })
        assert status == 422
        err_str = json.dumps(err_422)
        assert "123" not in err_str or "******" in err_str, f"Senha vazou na resposta 422: {err_str}"
        print("  -> Senha devidamente ocultada na resposta de erro de validação.")

        print("\n" + "=" * 60)
        print("TODOS OS 16 TESTES DE ISOLAMENTO E SEGURANÇA PASSARAM COM SUCESSO!")
        print("=" * 60)

    finally:
        # LIMPEZA OBRIGATÓRIA: Remover dados de teste do banco de dados
        print("\nExecutando limpeza completa de dados de teste do banco de dados...")
        session_db = get_session()
        try:
            usuarios_teste = session_db.query(Usuario).filter(Usuario.email.in_([EMAIL_A, EMAIL_B])).all()
            for u in usuarios_teste:
                session_db.delete(u)
            session_db.commit()
            print("-> Limpeza concluída com sucesso: nenhum dado de teste permaneceu no banco.")
        except Exception as e:
            session_db.rollback()
            print(f"Erro durante limpeza: {e}")
        finally:
            session_db.close()

        server.should_exit = True

if __name__ == "__main__":
    run_tests()
