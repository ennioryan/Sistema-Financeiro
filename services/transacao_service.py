from database import get_session
from models import Transacao, TipoTransacao
from datetime import date
import calendar

def criar_transacao(descricao, valor, tipo, categoria_id, data=None):
    session = get_session()
    try:
        nova = Transacao(
            descricao=descricao,
            valor=valor,
            tipo=TipoTransacao(tipo),
            categoria_id=categoria_id,
            data=data or date.today()
        )
        session.add(nova)
        session.commit()
        session.refresh(nova)
        return nova
    finally:
        session.close()

def listar_transacoes(mes=None, ano=None):
    session = get_session()
    try:
        query = session.query(Transacao)
        if mes and ano:
            ultimo_dia = calendar.monthrange(ano, mes)[1]
            query = query.filter(
                Transacao.data.between(date(ano, mes, 1), date(ano, mes, ultimo_dia))
            )
        return query.order_by(Transacao.data.desc()).all()
    finally:
        session.close()

def resumo_mensal(mes, ano):
    transacoes = listar_transacoes(mes, ano)
    receitas = sum(t.valor for t in transacoes if t.tipo == TipoTransacao.RECEITA)
    despesas = sum(t.valor for t in transacoes if t.tipo == TipoTransacao.DESPESA)
    return {
        "receitas": receitas,
        "despesas": despesas,
        "saldo": receitas - despesas
    }

def deletar_transacao(transacao_id):
    session = get_session()
    try:
        t = session.query(Transacao).filter_by(id=transacao_id).first()
        if t:
            session.delete(t)
            session.commit()
            return True
        return False
    finally:
        session.close()

def atualizar_transacao(transacao_id, descricao, valor, tipo, categoria_id, data=None):
    session = get_session()
    try:
        t = session.query(Transacao).filter_by(id=transacao_id).first()
        if t:
            t.descricao = descricao
            t.valor = valor
            t.tipo = TipoTransacao(tipo)
            t.categoria_id = categoria_id
            if data:
                t.data = data
            session.commit()
            session.refresh(t)
            return t
        return None
    finally:
        session.close()