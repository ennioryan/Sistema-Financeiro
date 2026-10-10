from database import get_session
from models import Transacao, TipoTransacao, Categoria
from datetime import date
import calendar

def criar_transacao(
    usuario_id: int,
    descricao: str,
    valor: float,
    tipo: str | TipoTransacao,
    categoria_id: int,
    data: date | None = None
) -> Transacao:
    """Cria uma nova transação vinculada obrigatoriamente ao usuário."""
    session = get_session()
    try:
        # Valida se a categoria existe e pertence ao usuário
        cat = session.query(Categoria).filter(
            Categoria.id == categoria_id,
            Categoria.usuario_id == usuario_id
        ).first()
        if not cat:
            raise ValueError("Categoria não encontrada ou não pertence ao usuário.")

        tipo_enum = TipoTransacao(tipo) if isinstance(tipo, str) else tipo
        nova = Transacao(
            descricao=descricao.strip(),
            valor=valor,
            tipo=tipo_enum,
            categoria_id=categoria_id,
            usuario_id=usuario_id,
            data=data or date.today()
        )
        session.add(nova)
        session.commit()
        session.refresh(nova)
        return nova
    finally:
        session.close()

def listar_transacoes(usuario_id: int, mes: int | None = None, ano: int | None = None) -> list[Transacao]:
    """Lista as transações pertencentes exclusivamente ao usuário."""
    session = get_session()
    try:
        query = session.query(Transacao).filter(Transacao.usuario_id == usuario_id)
        if mes and ano:
            ultimo_dia = calendar.monthrange(ano, mes)[1]
            query = query.filter(
                Transacao.data.between(date(ano, mes, 1), date(ano, mes, ultimo_dia))
            )
        return query.order_by(Transacao.data.desc(), Transacao.id.desc()).all()
    finally:
        session.close()

def resumo_mensal(usuario_id: int, mes: int, ano: int) -> dict:
    """Calcula o resumo mensal (receitas, despesas, saldo) para o usuário."""
    transacoes = listar_transacoes(usuario_id=usuario_id, mes=mes, ano=ano)
    receitas = sum(t.valor for t in transacoes if t.tipo == TipoTransacao.RECEITA)
    despesas = sum(t.valor for t in transacoes if t.tipo == TipoTransacao.DESPESA)
    return {
        "receitas": receitas,
        "despesas": despesas,
        "saldo": receitas - despesas
    }

def obter_transacao_por_id(usuario_id: int, transacao_id: int) -> Transacao | None:
    """Busca uma transação por ID garantindo que pertence ao usuário."""
    session = get_session()
    try:
        return session.query(Transacao).filter(
            Transacao.id == transacao_id,
            Transacao.usuario_id == usuario_id
        ).first()
    finally:
        session.close()

def deletar_transacao(usuario_id: int, transacao_id: int) -> bool:
    """Deleta uma transação pertencente exclusivamente ao usuário."""
    session = get_session()
    try:
        t = session.query(Transacao).filter(
            Transacao.id == transacao_id,
            Transacao.usuario_id == usuario_id
        ).first()
        if t:
            session.delete(t)
            session.commit()
            return True
        return False
    finally:
        session.close()

def atualizar_transacao(
    usuario_id: int,
    transacao_id: int,
    descricao: str,
    valor: float,
    tipo: str | TipoTransacao,
    categoria_id: int,
    data: date | None = None
) -> Transacao | None:
    """Atualiza uma transação pertencente exclusivamente ao usuário."""
    session = get_session()
    try:
        t = session.query(Transacao).filter(
            Transacao.id == transacao_id,
            Transacao.usuario_id == usuario_id
        ).first()
        if not t:
            return None

        # Valida se a categoria informada pertence ao usuário
        cat = session.query(Categoria).filter(
            Categoria.id == categoria_id,
            Categoria.usuario_id == usuario_id
        ).first()
        if not cat:
            raise ValueError("Categoria não encontrada ou não pertence ao usuário.")

        tipo_enum = TipoTransacao(tipo) if isinstance(tipo, str) else tipo
        t.descricao = descricao.strip()
        t.valor = valor
        t.tipo = tipo_enum
        t.categoria_id = categoria_id
        if data:
            t.data = data
        session.commit()
        session.refresh(t)
        return t
    finally:
        session.close()