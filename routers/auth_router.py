from fastapi import APIRouter, HTTPException, Depends, Response, status
from database import get_session
from models import Usuario, Categoria
from schemas.usuario import UsuarioCreate, UsuarioLogin, UsuarioResponse, TokenResponse
from services.auth_service import (
    gerar_hash_senha,
    verificar_senha,
    criar_access_token,
    definir_cookie_auth,
    remover_cookie_auth,
    get_current_user
)
from services import categoria_service

router = APIRouter(prefix="/api/auth", tags=["Autenticação"])

@router.post("/cadastro", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def cadastrar(dados: UsuarioCreate, response: Response):
    """Cadastra um novo usuário, cria suas categorias padrão e define o cookie de autenticação."""
    session = get_session()
    try:
        email_normalizado = dados.email.strip().lower()
        existente = session.query(Usuario).filter(Usuario.email == email_normalizado).first()
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="E-mail já cadastrado no sistema."
            )

        senha_hash = gerar_hash_senha(dados.senha)
        novo_usuario = Usuario(
            nome=dados.nome.strip(),
            email=email_normalizado,
            senha_hash=senha_hash
        )
        session.add(novo_usuario)
        session.flush()

        # Cria as categorias padrão para o novo usuário
        for nome_cat, tipo_cat in categoria_service.CATEGORIAS_PADRAO:
            cat = Categoria(
                nome=nome_cat,
                tipo=tipo_cat,
                usuario_id=novo_usuario.id
            )
            session.add(cat)

        session.commit()
        session.refresh(novo_usuario)

        token = criar_access_token({"sub": str(novo_usuario.id), "email": novo_usuario.email})
        definir_cookie_auth(response, token)

        usuario_resp = UsuarioResponse.model_validate(novo_usuario)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            usuario=usuario_resp
        )
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Erro interno ao realizar cadastro.")
    finally:
        session.close()

@router.post("/login", response_model=TokenResponse)
def login(dados: UsuarioLogin, response: Response):
    """Autentica o usuário com erro genérico e define o cookie de autenticação em caso de sucesso."""
    session = get_session()
    try:
        email_normalizado = dados.email.strip().lower()
        usuario = session.query(Usuario).filter(Usuario.email == email_normalizado).first()

        # Erro genérico "E-mail ou senha inválidos" (401), sem revelar qual dos dois errou
        if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="E-mail ou senha inválidos"
            )

        token = criar_access_token({"sub": str(usuario.id), "email": usuario.email})
        definir_cookie_auth(response, token)

        usuario_resp = UsuarioResponse.model_validate(usuario)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            usuario=usuario_resp
        )
    finally:
        session.close()

@router.post("/logout")
def logout(response: Response):
    """Remove o cookie de autenticação."""
    remover_cookie_auth(response)
    return {"message": "Logout realizado com sucesso"}

@router.get("/me", response_model=UsuarioResponse)
def get_me(current_user: Usuario = Depends(get_current_user)):
    """Retorna os dados do usuário autenticado (sem senha ou hash)."""
    return current_user
