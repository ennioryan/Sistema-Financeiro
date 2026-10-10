from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from services.auth_service import decodificar_access_token
from database import get_session
from models import Usuario

router = APIRouter(tags=["Views"])
templates = Jinja2Templates(directory="templates")

def obter_usuario_logado(request: Request) -> Usuario | None:
    """Verifica se há um usuário autenticado através do cookie access_token."""
    token = request.cookies.get("access_token")
    if not token:
        return None

    if token.startswith("Bearer ") or token.startswith("bearer "):
        token = token.split(" ", 1)[1]
    token = token.strip()
    if not token:
        return None

    payload = decodificar_access_token(token)
    if not payload:
        return None

    user_id_raw = payload.get("sub") or payload.get("id")
    if not user_id_raw:
        return None

    try:
        user_id = int(user_id_raw)
    except (ValueError, TypeError):
        return None

    session = get_session()
    try:
        usuario = session.query(Usuario).filter(Usuario.id == user_id).first()
        if usuario:
            session.expunge(usuario)
        return usuario
    finally:
        session.close()

@router.get("/", response_class=HTMLResponse)
def get_dashboard(request: Request):
    usuario = obter_usuario_logado(request)
    if not usuario:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request=request, name="index.html", context={"usuario": usuario})

@router.get("/login", response_class=HTMLResponse)
def get_login(request: Request):
    usuario = obter_usuario_logado(request)
    if usuario:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="login.html")

@router.get("/cadastro", response_class=HTMLResponse)
def get_cadastro(request: Request):
    usuario = obter_usuario_logado(request)
    if usuario:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="cadastro.html")
