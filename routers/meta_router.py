from fastapi import APIRouter, HTTPException
from schemas.meta import MetaCreate, MetaUpdateProgresso, Meta as MetaSchema
from services import meta_service

router = APIRouter(prefix="/api/metas", tags=["Metas"])

@router.post("", response_model=MetaSchema)
def criar_meta(meta: MetaCreate):
    try:
        return meta_service.criar_meta(
            nome=meta.nome,
            valor_alvo=meta.valor_alvo,
            prazo=meta.prazo
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=list[MetaSchema])
def listar_metas():
    try:
        return meta_service.listar_metas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{id}/progresso", response_model=MetaSchema)
def atualizar_progresso(id: int, update: MetaUpdateProgresso):
    try:
        meta = meta_service.atualizar_progresso(meta_id=id, valor=update.valor)
        if not meta:
            raise HTTPException(status_code=404, detail="Meta não encontrada")
        return meta
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
