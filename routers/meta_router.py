from fastapi import APIRouter, HTTPException, Depends
from schemas.meta import MetaCreate, MetaUpdateProgresso, Meta as MetaSchema
from services import meta_service
from services.auth_service import get_current_user
from models import Usuario

router = APIRouter(prefix="/api/metas", tags=["Metas"])

@router.post("", response_model=MetaSchema)
def criar_meta(
    meta: MetaCreate,
    current_user: Usuario = Depends(get_current_user)
):
    try:
        return meta_service.criar_meta(
            usuario_id=current_user.id,
            nome=meta.nome,
            valor_alvo=meta.valor_alvo,
            prazo=meta.prazo
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=list[MetaSchema])
def listar_metas(current_user: Usuario = Depends(get_current_user)):
    try:
        return meta_service.listar_metas(usuario_id=current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{id}/progresso", response_model=MetaSchema)
def atualizar_progresso(
    id: int,
    update: MetaUpdateProgresso,
    current_user: Usuario = Depends(get_current_user)
):
    try:
        meta = meta_service.atualizar_progresso(
            usuario_id=current_user.id,
            meta_id=id,
            valor=update.valor
        )
        if not meta:
            raise HTTPException(status_code=404, detail="Meta não encontrada")
        return meta
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
