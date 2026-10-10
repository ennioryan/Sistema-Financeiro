from fastapi import APIRouter, HTTPException, Query, Depends
from schemas.transacao import TransacaoCreate, Transacao as TransacaoSchema, ResumoMensal
from services import transacao_service
from services.auth_service import get_current_user
from models import Usuario

router = APIRouter(prefix="/api/transacoes", tags=["Transações"])

@router.post("", response_model=TransacaoSchema)
def criar_transacao(
    transacao: TransacaoCreate,
    current_user: Usuario = Depends(get_current_user)
):
    try:
        return transacao_service.criar_transacao(
            usuario_id=current_user.id,
            descricao=transacao.descricao,
            valor=transacao.valor,
            tipo=transacao.tipo.value,
            categoria_id=transacao.categoria_id,
            data=transacao.data
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=list[TransacaoSchema])
def listar_transacoes(
    mes: int | None = None,
    ano: int | None = None,
    current_user: Usuario = Depends(get_current_user)
):
    try:
        return transacao_service.listar_transacoes(
            usuario_id=current_user.id,
            mes=mes,
            ano=ano
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/resumo", response_model=ResumoMensal)
def resumo_mensal(
    mes: int = Query(..., ge=1, le=12),
    ano: int = Query(..., ge=1900),
    current_user: Usuario = Depends(get_current_user)
):
    try:
        return transacao_service.resumo_mensal(
            usuario_id=current_user.id,
            mes=mes,
            ano=ano
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id}")
def deletar_transacao(
    id: int,
    current_user: Usuario = Depends(get_current_user)
):
    try:
        sucesso = transacao_service.deletar_transacao(
            usuario_id=current_user.id,
            transacao_id=id
        )
        if not sucesso:
            raise HTTPException(status_code=404, detail="Transação não encontrada")
        return {"success": True, "message": "Transação deletada com sucesso"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id}", response_model=TransacaoSchema)
def atualizar_transacao(
    id: int,
    transacao: TransacaoCreate,
    current_user: Usuario = Depends(get_current_user)
):
    try:
        t = transacao_service.atualizar_transacao(
            usuario_id=current_user.id,
            transacao_id=id,
            descricao=transacao.descricao,
            valor=transacao.valor,
            tipo=transacao.tipo.value,
            categoria_id=transacao.categoria_id,
            data=transacao.data
        )
        if not t:
            raise HTTPException(status_code=404, detail="Transação não encontrada")
        return t
    except HTTPException as he:
        raise he
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
