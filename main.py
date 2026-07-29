from database import engine, Base
from services import transacao_service, categoria_service, meta_service
from relatorios import graficos
from tabulate import tabulate

Base.metadata.create_all(engine)

def menu():
    while True:
        print("\n=== SISTEMA FINANCEIRO PESSOAL ===")
        print("1. Nova transação")
        print("2. Listar transações")
        print("3. Nova categoria")
        print("4. Resumo mensal")
        print("5. Gráfico de despesas por categoria")
        print("6. Nova meta")
        print("7. Listar metas")
        print("0. Sair")

        opcao = input("Escolha: ")

        if opcao == "1":
            desc = input("Descrição: ")
            valor = float(input("Valor: "))
            tipo = input("Tipo (receita/despesa): ")
            cats = categoria_service.listar_categorias()
            for c in cats:
                print(f"{c.id} - {c.nome}")
            cat_id = int(input("ID da categoria: "))
            transacao_service.criar_transacao(desc, valor, tipo, cat_id)
            print("Transação criada!")

        elif opcao == "2":
            transacoes = transacao_service.listar_transacoes()
            tabela = [[t.id, t.descricao, t.valor, t.tipo.value, t.data] for t in transacoes]
            print(tabulate(tabela, headers=["ID", "Descrição", "Valor", "Tipo", "Data"]))

        elif opcao == "3":
            nome = input("Nome da categoria: ")
            tipo = input("Tipo (receita/despesa): ")
            categoria_service.criar_categoria(nome, tipo)
            print("Categoria criada!")

        elif opcao == "4":
            mes = int(input("Mês: "))
            ano = int(input("Ano: "))
            resumo = transacao_service.resumo_mensal(mes, ano)
            print(f"Receitas: R$ {resumo['receitas']:.2f}")
            print(f"Despesas: R$ {resumo['despesas']:.2f}")
            print(f"Saldo: R$ {resumo['saldo']:.2f}")

        elif opcao == "5":
            transacoes = transacao_service.listar_transacoes()
            graficos.grafico_pizza_categorias(transacoes)
            print("Gráfico salvo como relatorio_categorias.png")

        elif opcao == "6":
            nome = input("Nome da meta: ")
            valor = float(input("Valor alvo: "))
            meta_service.criar_meta(nome, valor)
            print("Meta criada!")

        elif opcao == "7":
            metas = meta_service.listar_metas()
            for m in metas:
                progresso = (m.valor_atual / m.valor_alvo) * 100 if m.valor_alvo else 0
                print(f"{m.nome}: R$ {m.valor_atual:.2f}/{m.valor_alvo:.2f} ({progresso:.1f}%)")

        elif opcao == "0":
            break

if __name__ == "__main__":
    menu()