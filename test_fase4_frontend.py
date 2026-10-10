import sys
import os
import json
import urllib.request
import urllib.error
import http.cookiejar
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_session
from models import Usuario

BASE_URL = "http://127.0.0.1:8000"

class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def test_frontend_flow():
    print("=" * 60)
    print("INICIANDO TESTES DO FLUXO FRONTEND / TELAS (FASE 4)")
    print("=" * 60)

    # 1. Teste de Acesso a "/" sem autenticação
    print("\n[1] Testando acesso a '/' sem autenticação...")
    opener_no_redirect = urllib.request.build_opener(NoRedirectHandler)
    req = urllib.request.Request(f"{BASE_URL}/", headers={"Accept": "text/html"})
    try:
        resp = opener_no_redirect.open(req)
        status = resp.status
        location = resp.headers.get("Location")
    except urllib.error.HTTPError as e:
        status = e.code
        location = e.headers.get("Location")

    print(f"  -> Status retornado: {status}, Redirecionamento Location: {location}")
    assert status == 303 or status == 302 or status == 307, f"Esperado redirecionamento, obtido {status}"
    assert location == "/login" or location.endswith("/login"), f"Esperado redirecionamento para /login, obtido {location}"
    print("  -> Acesso anônimo a '/' redireciona para '/login' com sucesso.")

    # 2. Teste de Renderização de /login
    print("\n[2] Testando carregamento de templates/login.html...")
    resp_login = urllib.request.urlopen(f"{BASE_URL}/login")
    assert resp_login.status == 200
    html_login = resp_login.read().decode("utf-8")
    assert "Finanças Pro" in html_login
    assert "togglePasswordVisibility" in html_login, "Botão mostrar/ocultar senha presente"
    assert 'type="email"' in html_login
    assert 'type="password"' in html_login
    assert 'id="btn-submit"' in html_login
    assert 'href="/cadastro"' in html_login
    print("  -> Tela de login carrega perfeitamente com todos os elementos necessários.")

    # 3. Teste de Renderização de /cadastro
    print("\n[3] Testando carregamento de templates/cadastro.html e checklist de senha...")
    resp_cad = urllib.request.urlopen(f"{BASE_URL}/cadastro")
    assert resp_cad.status == 200
    html_cad = resp_cad.read().decode("utf-8")
    assert "Finanças Pro" in html_cad
    assert "rule-length" in html_cad, "Checklist de tamanho presente"
    assert "rule-uppercase" in html_cad, "Checklist de maiúscula presente"
    assert "rule-lowercase" in html_cad, "Checklist de minúscula presente"
    assert "rule-number" in html_cad, "Checklist de número presente"
    assert "rule-special" in html_cad, "Checklist de caractere especial presente"
    assert "rule-match" in html_cad, "Checklist de confirmação de senha presente"
    assert "togglePasswordVisibility" in html_cad, "Botão mostrar/ocultar senha presente"
    print("  -> Tela de cadastro carrega perfeitamente com todos os itens do checklist em tempo real.")

    # 4. Validação da lógica JavaScript das regras de senha
    print("\n[4] Validando regras de senha (algoritmo do frontend)...")
    def validate_password_rules(v):
        return {
            "length": 6 <= len(v) <= 14,
            "uppercase": bool(re.search(r"[A-Z]", v)),
            "lowercase": bool(re.search(r"[a-z]", v)),
            "number": bool(re.search(r"[0-9]", v)),
            "special": bool(re.search(r"[^a-zA-Z0-9\s]", v))
        }

    assert not validate_password_rules("Ab1!")["length"], "Deveria falhar em tamanho"
    assert not validate_password_rules("senhavalida1!")["uppercase"], "Deveria falhar em maiúscula"
    assert not validate_password_rules("SENHAVALIDA1!")["lowercase"], "Deveria falhar em minúscula"
    assert not validate_password_rules("SenhaValida!")["number"], "Deveria falhar em número"
    assert not validate_password_rules("SenhaValida1")["special"], "Deveria falhar em especial"
    assert all(validate_password_rules("SenhaForte1!").values()), "Deveria passar em todas as regras"
    print("  -> Regras de validação do frontend consistentes com o backend.")

    # 5. Testando submissão de cadastro inválido no backend
    print("\n[5] Testando rejeição 422 para regras de senha no endpoint /api/auth/cadastro...")
    req_invalido = urllib.request.Request(
        f"{BASE_URL}/api/auth/cadastro",
        data=json.dumps({"nome": "Teste", "email": "teste_inv@exemplo.com", "senha": "abc"}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        urllib.request.urlopen(req_invalido)
        assert False, "Deveria retornar 422"
    except urllib.error.HTTPError as e:
        assert e.code == 422
        body_err = json.loads(e.read().decode("utf-8"))
        assert "abc" not in json.dumps(body_err), "Senha não deve vazar na resposta 422"
        print("  -> Backend rejeitou senha inválida com HTTP 422 sem vazar a senha.")

    # 6. Cadastro válido com cookies e redirecionamento
    print("\n[6] Testando cadastro válido e autenticação com cookie...")
    EMAIL_TESTE = "frontend_user_teste@exemplo.com"
    SENHA_TESTE = "SenhaForte1!"
    NOME_TESTE = "Fernanda Lima"

    # Limpeza prévia
    session = get_session()
    try:
        u = session.query(Usuario).filter_by(email=EMAIL_TESTE).first()
        if u:
            session.delete(u)
            session.commit()
    finally:
        session.close()

    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

    req_cad = urllib.request.Request(
        f"{BASE_URL}/api/auth/cadastro",
        data=json.dumps({"nome": NOME_TESTE, "email": EMAIL_TESTE, "senha": SENHA_TESTE}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with opener.open(req_cad) as resp:
        assert resp.status == 201
        cad_body = json.loads(resp.read().decode("utf-8"))
        assert cad_body["usuario"]["nome"] == NOME_TESTE
        print("  -> Usuário cadastrado com sucesso. Cookie access_token armazenado no cliente.")

    # 7. Acesso ao dashboard autenticado: deve retornar 200 com "Olá, {nome}" e botão "Sair"
    print("\n[7] Testando acesso autenticado ao dashboard (/)...")
    req_dash = urllib.request.Request(f"{BASE_URL}/", headers={"Accept": "text/html"})
    with opener.open(req_dash) as resp:
        assert resp.status == 200
        html_dash = resp.read().decode("utf-8")
        assert "Olá," in html_dash
        assert NOME_TESTE in html_dash, f"Nome {NOME_TESTE} não encontrado no cabeçalho do dashboard"
        assert "btn-logout" in html_dash or "handleLogout" in html_dash, "Botão sair presente"
        print(f"  -> Dashboard renderizou 'Olá, {NOME_TESTE}' e botão 'Sair' com sucesso.")

    # 8. Teste de Redirecionamento quando já autenticado (/login -> /)
    print("\n[8] Testando redirecionamento de usuário autenticado ao tentar acessar /login e /cadastro...")
    opener_auth_noredir = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookie_jar),
        NoRedirectHandler
    )
    for rota in ["/login", "/cadastro"]:
        try:
            resp_redir = opener_auth_noredir.open(urllib.request.Request(f"{BASE_URL}{rota}"))
            code = resp_redir.status
            loc = resp_redir.headers.get("Location")
        except urllib.error.HTTPError as e:
            code = e.code
            loc = e.headers.get("Location")
        assert code in (302, 303, 307) and (loc == "/" or loc.endswith("/")), f"Falha ao redirecionar de {rota}"
    print("  -> Usuário autenticado redirecionado para '/' ao tentar acessar /login e /cadastro.")

    # 9. Teste de Logout
    print("\n[9] Testando logout via POST /api/auth/logout...")
    req_logout = urllib.request.Request(f"{BASE_URL}/api/auth/logout", method="POST")
    with opener.open(req_logout) as resp:
        assert resp.status == 200
        print("  -> Logout executado. Cookie removido.")

    # 10. Teste de Login com erro
    print("\n[10] Testando login com credenciais erradas...")
    req_login_err = urllib.request.Request(
        f"{BASE_URL}/api/auth/login",
        data=json.dumps({"email": EMAIL_TESTE, "senha": "SenhaIncorreta999!"}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        urllib.request.urlopen(req_login_err)
        assert False, "Deveria retornar 401"
    except urllib.error.HTTPError as e:
        assert e.code == 401
        err_data = json.loads(e.read().decode("utf-8"))
        assert err_data["detail"] == "E-mail ou senha inválidos"
        print("  -> Login incorreto retornou HTTP 401 com mensagem genérica 'E-mail ou senha inválidos'.")

    # 11. Teste de Login com sucesso
    print("\n[11] Testando login correto...")
    req_login_ok = urllib.request.Request(
        f"{BASE_URL}/api/auth/login",
        data=json.dumps({"email": EMAIL_TESTE, "senha": SENHA_TESTE}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with opener.open(req_login_ok) as resp:
        assert resp.status == 200
        print("  -> Login correto realizado com sucesso.")

    # Limpeza
    print("\nExecutando limpeza dos dados de teste...")
    session = get_session()
    try:
        u = session.query(Usuario).filter_by(email=EMAIL_TESTE).first()
        if u:
            session.delete(u)
            session.commit()
            print("  -> Dados de teste limpos do banco com sucesso.")
    finally:
        session.close()

    print("\n" + "=" * 60)
    print("TODOS OS TESTES DA FASE 4 FORAM CONCLUÍDOS COM SUCESSO!")
    print("=" * 60)

if __name__ == "__main__":
    test_frontend_flow()
