"""
Script de migração do banco de dados para a Fase 2.
Responsável por resetar e recriar as tabelas do sistema financeiro com suporte a multi-usuários.

AVISO:
- Dropará apenas as tabelas: 'transacoes', 'metas' e 'categorias'.
- Criará as tabelas: 'usuarios', 'categorias', 'transacoes' e 'metas' com isolamento por usuario_id.
- As credenciais de conexão são carregadas exclusivamente do arquivo .env (via database.py).
"""

import sys
import logging
from sqlalchemy import text, inspect
from database import engine, Base
import models  # Carrega os modelos registrados no Base.metadata

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("migrar_banco")

def migrar():
    logger.info("Iniciando processo de migração e reset limpo...")
    
    # 1. Dropar EXCLUSIVAMENTE as três tabelas especificadas
    tabelas_para_dropar = ["transacoes", "metas", "categorias"]
    
    with engine.begin() as conn:
        for tabela in tabelas_para_dropar:
            logger.info(f"Removendo tabela (se existir): {tabela}")
            conn.execute(text(f"DROP TABLE IF EXISTS {tabela} CASCADE;"))
    
    logger.info("Tabelas antigas removidas com sucesso.")
    
    # 2. Criar todas as tabelas com os novos esquemas (usuarios, categorias, transacoes, metas)
    logger.info("Criando novas tabelas a partir dos modelos (models.py)...")
    Base.metadata.create_all(engine)
    
    # 3. Inspecionar e confirmar as tabelas criadas
    inspector = inspect(engine)
    tabelas_finais = inspector.get_table_names()
    logger.info(f"Tabelas presentes no banco de dados agora: {tabelas_finais}")
    
    logger.info("Migração concluída com sucesso!")

if __name__ == "__main__":
    confirmacao = input("ATENÇÃO: Este script irá apagar os dados de 'transacoes', 'metas' e 'categorias'. Deseja continuar? (s/N): ")
    if confirmacao.strip().lower() in ("s", "sim", "y", "yes"):
        migrar()
    else:
        logger.info("Migração cancelada pelo usuário.")
        sys.exit(0)
