from database import get_session
from models import Meta

def criar_meta(nome, valor_alvo, prazo=None):
    session = get_session()
    try:
        meta = Meta(nome=nome, valor_alvo=valor_alvo, prazo=prazo)
        session.add(meta)
        session.commit()
        session.refresh(meta)
        return meta
    finally:
        session.close()

def atualizar_progresso(meta_id, valor):
    session = get_session()
    try:
        meta = session.query(Meta).filter_by(id=meta_id).first()
        if meta:
            meta.valor_atual += valor
            session.commit()
        return meta
    finally:
        session.close()

def listar_metas():
    session = get_session()
    try:
        return session.query(Meta).all()
    finally:
        session.close()