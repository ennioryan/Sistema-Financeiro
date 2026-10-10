from fastapi import APIRouter, HTTPException, Depends
from schemas.categoria import CategoriaCreate, Categoria as CategoriaSchema
from services import categoria_service
from services.auth_service import get_current_user
from models import Usuario

router = APIRouter(prefix="/api/categorias", tags=["Categorias"])

@router.post("", response_model=CategoriaSchema)
def criar_categoria(
    categoria: CategoriaCreate,
    current_user: Usuario = Depends(get_current_user)
):
    try:
        return categoria_service.criar_categoria(
            usuario_id=current_user.id,
            nome=categoria.nome,
            tipo=categoria.tipo.value
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=list[CategoriaSchema])
def listar_categorias(current_user: Usuario = Depends(get_current_user)):
    try:
        return categoria_service.listar_categorias(usuario_id=current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
