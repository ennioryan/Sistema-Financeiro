from pydantic import BaseModel
from datetime import date

class MetaBase(BaseModel):
    nome: str
    valor_alvo: float
    prazo: date | None = None

class MetaCreate(MetaBase):
    pass

class MetaUpdateProgresso(BaseModel):
    valor: float

class Meta(MetaBase):
    id: int
    valor_atual: float

    class Config:
        from_attributes = True
