from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum
import datetime

class TipoTransacao(enum.Enum):
    RECEITA = "receita"
    DESPESA = "despesa"

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True)
    nome = Column(String(50), nullable=False)
    tipo = Column(Enum(TipoTransacao), nullable=False)

    transacoes = relationship("Transacao", back_populates="categoria")

class Transacao(Base):
    __tablename__ = "transacoes"

    id = Column(Integer, primary_key=True)
    descricao = Column(String(200), nullable=False)
    valor = Column(Float, nullable=False)
    tipo = Column(Enum(TipoTransacao), nullable=False)
    data = Column(Date, default=datetime.date.today)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))

    categoria = relationship("Categoria", back_populates="transacoes")

class Meta(Base):
    __tablename__ = "metas"

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    valor_alvo = Column(Float, nullable=False)
    valor_atual = Column(Float, default=0.0)
    prazo = Column(Date, nullable=True)