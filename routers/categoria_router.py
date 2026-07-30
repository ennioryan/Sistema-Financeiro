from fastapi import APIRouter, HTTPException
from schemas.categoria import CategoriaCreate, Categoria as CategoriaSchema
from services import categoria_service

router = APIRouter(prefix="/api/categorias", tags=["Categorias"])

@router.post("", response_model=CategoriaSchema)
def criar_categoria(categoria: CategoriaCreate):
    try:
        # Categoria tipo is a TipoTransacao enum. We pass its value.
        return categoria_service.criar_categoria(categoria.nome, categoria.tipo.value)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=list[CategoriaSchema])
def listar_categorias():
    try:
        return categoria_service.listar_categorias()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
