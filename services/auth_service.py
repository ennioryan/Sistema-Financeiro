import os
import datetime
from datetime import timezone, timedelta
from typing import Optional, Any
import bcrypt
import jwt
from fastapi import Response, Request, HTTPException
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("A variável de ambiente SECRET_KEY não está configurada no .env.")

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))  # Padrão: 7 dias
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").strip().lower() in ("true", "1", "yes")

def gerar_hash_senha(senha: str) -> str:
    """Gera o hash da senha usando bcrypt com salt aleatório."""
    salt = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(senha.encode("utf-8"), salt)
    return hash_bytes.decode("utf-8")

def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    """Verifica se a senha em texto plano confere com o hash armazenado."""
    try:
        return bcrypt.checkpw(senha_plana.encode("utf-8"), senha_hash.encode("utf-8"))
    except Exception:
        return False

def criar_access_token(dados: dict[str, Any], expira_em: Optional[timedelta] = None) -> str:
    """Cria um token JWT assinado contendo os dados fornecidos e data de expiração."""
    payload = dados.copy()
    agora = datetime.datetime.now(timezone.utc)
    if expira_em:
        expiracao = agora + expira_em
    else:
        expiracao = agora + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload.update({"exp": expiracao, "iat": agora})
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decodificar_access_token(token: str) -> Optional[dict[str, Any]]:
    """Decodifica e valida o token JWT. Retorna o payload se válido, ou None se inválido/expirado."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except (jwt.ExpiredSignatureError, jwt.PyJWTError):
        return None

def definir_cookie_auth(response: Response, token: str) -> None:
    """Configura o cookie de autenticação HttpOnly com os parâmetros de segurança definidos."""
    # max_age em segundos
    max_age_segundos = ACCESS_TOKEN_EXPIRE_MINUTES * 60
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        samesite="lax",
        secure=COOKIE_SECURE,
        max_age=max_age_segundos,
        path="/"
    )

def remover_cookie_auth(response: Response) -> None:
    """Remove o cookie de autenticação ao efetuar logout."""
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True,
        samesite="lax",
        secure=COOKIE_SECURE
    )

def get_current_user(request: Request) -> Any:
    """Dependência FastAPI para autenticar usuário a partir do cookie access_token (ou header)."""
    from database import get_session
    from models import Usuario

    token = request.cookies.get("access_token")
    if not token:
        # Fallback para cabeçalho Authorization se presente (ex: requisições API/testes)
        auth_header = request.headers.get("Authorization")
        if auth_header and (auth_header.startswith("Bearer ") or auth_header.startswith("bearer ")):
            token = auth_header.split(" ", 1)[1]

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Autenticação necessária. Token de acesso ausente."
        )

    if token.startswith("Bearer ") or token.startswith("bearer "):
        token = token.split(" ", 1)[1]
    token = token.strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Token de autenticação inválido."
        )

    payload = decodificar_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado."
        )

    user_id_raw = payload.get("sub") or payload.get("id")
    if not user_id_raw:
        raise HTTPException(
            status_code=401,
            detail="Token inválido: identificador de usuário ausente."
        )

    try:
        user_id = int(user_id_raw)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Token inválido: formato do identificador incorreto."
        )

    session = get_session()
    try:
        usuario = session.query(Usuario).filter(Usuario.id == user_id).first()
        if not usuario:
            raise HTTPException(
                status_code=401,
                detail="Usuário não encontrado."
            )
        session.expunge(usuario)
        return usuario
    finally:
        session.close()

