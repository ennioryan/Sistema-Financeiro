from database import get_session
from models import Categoria, TipoTransacao

CATEGORIAS_PADRAO = [
    ("Alimentação", TipoTransacao.DESPESA),
    ("Transporte", TipoTransacao.DESPESA),
    ("Moradia", TipoTransacao.DESPESA),
    ("Lazer", TipoTransacao.DESPESA),
    ("Salário", TipoTransacao.RECEITA),
    ("Investimentos", TipoTransacao.RECEITA),
]

def criar_categoria(usuario_id: int, nome: str, tipo: str | TipoTransacao) -> Categoria:
    """Cria uma categoria vinculada obrigatoriamente ao usuário."""
    session = get_session()
    try:
        tipo_enum = TipoTransacao(tipo) if isinstance(tipo, str) else tipo
        cat = Categoria(
            usuario_id=usuario_id,
            nome=nome.strip(),
            tipo=tipo_enum
        )
        session.add(cat)
        session.commit()
        session.refresh(cat)
        return cat
    finally:
        session.close()

def listar_categorias(usuario_id: int) -> list[Categoria]:
    """Lista todas as categorias pertencentes exclusivamente ao usuário."""
    session = get_session()
    try:
        return session.query(Categoria).filter(
            Categoria.usuario_id == usuario_id
        ).order_by(Categoria.nome.asc()).all()
    finally:
        session.close()

def buscar_categoria(usuario_id: int, categoria_id: int) -> Categoria | None:
    """Busca uma categoria por ID garantindo que pertence ao usuário."""
    session = get_session()
    try:
        return session.query(Categoria).filter(
            Categoria.id == categoria_id,
            Categoria.usuario_id == usuario_id
        ).first()
    finally:
        session.close()

def criar_categorias_padrao(usuario_id: int, session=None) -> list[Categoria]:
    """Cria as categorias padrão do usuário recém-cadastrado."""
    fecha_sessao = False
    if session is None:
        session = get_session()
        fecha_sessao = True

    try:
        criadas = []
        for nome, tipo in CATEGORIAS_PADRAO:
            cat = Categoria(
                nome=nome,
                tipo=tipo,
                usuario_id=usuario_id
            )
            session.add(cat)
            criadas.append(cat)
        session.commit()
        for cat in criadas:
            session.refresh(cat)
        return criadas
    except Exception:
        session.rollback()
        raise
    finally:
        if fecha_sessao:
            session.close()