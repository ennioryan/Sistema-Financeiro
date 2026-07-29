import matplotlib.pyplot as plt
from models import TipoTransacao

def grafico_pizza_categorias(transacoes):
    despesas = [t for t in transacoes if t.tipo == TipoTransacao.DESPESA]
    dados = {}
    for t in despesas:
        nome_cat = t.categoria.nome if t.categoria else "Sem categoria"
        dados[nome_cat] = dados.get(nome_cat, 0) + t.valor

    plt.figure(figsize=(7, 7))
    plt.pie(dados.values(), labels=dados.keys(), autopct="%1.1f%%")
    plt.title("Despesas por Categoria")
    plt.savefig("relatorio_categorias.png")
    plt.close()

def grafico_evolucao_mensal(resumos_por_mes):
    meses = list(resumos_por_mes.keys())
    saldos = [r["saldo"] for r in resumos_por_mes.values()]

    plt.figure(figsize=(10, 5))
    plt.plot(meses, saldos, marker="o")
    plt.title("Evolução do Saldo Mensal")
    plt.xlabel("Mês")
    plt.ylabel("Saldo (R$)")
    plt.grid(True)
    plt.savefig("relatorio_evolucao.png")
    plt.close()