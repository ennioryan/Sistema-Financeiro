from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base
import enum
import datetime

class TipoTransacao(enum.Enum):
    RECEITA = "receita"
    DESPESA = "despesa"

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    criado_em = Column(DateTime, default=datetime.datetime.utcnow)

    transacoes = relationship("Transacao", back_populates="usuario", cascade="all, delete-orphan")
    categorias = relationship("Categoria", back_populates="usuario", cascade="all, delete-orphan")
    metas = relationship("Meta", back_populates="usuario", cascade="all, delete-orphan")

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True)
    nome = Column(String(50), nullable=False)
    tipo = Column(Enum(TipoTransacao), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)

    usuario = relationship("Usuario", back_populates="categorias")
    transacoes = relationship("Transacao", back_populates="categoria")

    __table_args__ = (
        UniqueConstraint("usuario_id", "nome", name="uq_usuario_categoria_nome"),
    )

class Transacao(Base):
    __tablename__ = "transacoes"

    id = Column(Integer, primary_key=True)
    descricao = Column(String(200), nullable=False)
    valor = Column(Float, nullable=False)
    tipo = Column(Enum(TipoTransacao), nullable=False)
    data = Column(Date, default=datetime.date.today)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)

    usuario = relationship("Usuario", back_populates="transacoes")
    categoria = relationship("Categoria", back_populates="transacoes", lazy="joined")

class Meta(Base):
    __tablename__ = "metas"

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    valor_alvo = Column(Float, nullable=False)
    valor_atual = Column(Float, default=0.0)
    prazo = Column(Date, nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)

    usuario = relationship("Usuario", back_populates="metas")