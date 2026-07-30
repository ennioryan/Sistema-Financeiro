from pydantic import BaseModel
from datetime import date
from models import TipoTransacao
from schemas.categoria import Categoria

class TransacaoBase(BaseModel):
    descricao: str
    valor: float
    tipo: TipoTransacao
    categoria_id: int
    data: date | None = None

class TransacaoCreate(TransacaoBase):
    pass

class Transacao(TransacaoBase):
    id: int
    categoria: Categoria | None = None

    class Config:
        from_attributes = True

class ResumoMensal(BaseModel):
    receitas: float
    despesas: float
    saldo: float
