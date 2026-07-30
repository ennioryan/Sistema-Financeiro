from pydantic import BaseModel
from models import TipoTransacao

class CategoriaBase(BaseModel):
    nome: str
    tipo: TipoTransacao

class CategoriaCreate(CategoriaBase):
    pass

class Categoria(CategoriaBase):
    id: int

    class Config:
        from_attributes = True
