from database import get_session
from models import Categoria, TipoTransacao

def criar_categoria(nome, tipo):
    session = get_session()
    try:
        cat = Categoria(nome=nome, tipo=TipoTransacao(tipo))
        session.add(cat)
        session.commit()
        session.refresh(cat)
        return cat
    finally:
        session.close()

def listar_categorias():
    session = get_session()
    try:
        return session.query(Categoria).all()
    finally:
        session.close()