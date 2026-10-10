from database import get_session
from models import Meta
from datetime import date

def criar_meta(usuario_id: int, nome: str, valor_alvo: float, prazo: date | None = None) -> Meta:
    """Cria uma nova meta associada obrigatoriamente ao usuário."""
    session = get_session()
    try:
        meta = Meta(
            usuario_id=usuario_id,
            nome=nome.strip(),
            valor_alvo=valor_alvo,
            prazo=prazo
        )
        session.add(meta)
        session.commit()
        session.refresh(meta)
        return meta
    finally:
        session.close()

def obter_meta_por_id(usuario_id: int, meta_id: int) -> Meta | None:
    """Busca uma meta por ID pertencente exclusivamente ao usuário."""
    session = get_session()
    try:
        return session.query(Meta).filter(
            Meta.id == meta_id,
            Meta.usuario_id == usuario_id
        ).first()
    finally:
        session.close()

def atualizar_progresso(usuario_id: int, meta_id: int, valor: float) -> Meta | None:
    """Atualiza o progresso financeiro de uma meta pertencente ao usuário."""
    session = get_session()
    try:
        meta = session.query(Meta).filter(
            Meta.id == meta_id,
            Meta.usuario_id == usuario_id
        ).first()
        if meta:
            meta.valor_atual += valor
            session.commit()
            session.refresh(meta)
        return meta
    finally:
        session.close()

def listar_metas(usuario_id: int) -> list[Meta]:
    """Lista todas as metas pertencentes exclusivamente ao usuário."""
    session = get_session()
    try:
        return session.query(Meta).filter(
            Meta.usuario_id == usuario_id
        ).order_by(Meta.id.asc()).all()
    finally:
        session.close()

def deletar_meta(usuario_id: int, meta_id: int) -> bool:
    """Deleta uma meta pertencente exclusivamente ao usuário."""
    session = get_session()
    try:
        meta = session.query(Meta).filter(
            Meta.id == meta_id,
            Meta.usuario_id == usuario_id
        ).first()
        if meta:
            session.delete(meta)
            session.commit()
            return True
        return False
    finally:
        session.close()