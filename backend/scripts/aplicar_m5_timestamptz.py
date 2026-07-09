# Aplica a mudança incremental do item M5: converte as colunas de data/hora do banco de dev de
# TIMESTAMP (naive) para TIMESTAMPTZ, interpretando os valores existentes como UTC (que é como
# o datetime.utcnow antigo os gravava). Sem isso, os modelos novos — DateTime(timezone=True) +
# agoraUtc() — falham ao gravar em coluna naive (asyncpg rejeita datetime com tzinfo).
# Idempotente: converter uma coluna que já é timestamptz não altera nada.
#
# Como usar a partir de backend/ (ou via docker compose exec backend):
#   python scripts/aplicar_m5_timestamptz.py

import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.banco_dados import engine

# Todas as colunas de data/hora dos modelos atuais (tabela → colunas)
COLUNAS_DATA_HORA = {
    "Empresas": ["Criacao"],
    "Condominios": ["Criacao"],
    "Usuarios": ["Criacao"],
    "Chamados": ["PrazoSLA", "Criacao", "Atualizacao"],
    "Mensagens": ["Criacao"],
}


async def main():
    async with engine.begin() as conn:
        for tabela, colunas in COLUNAS_DATA_HORA.items():
            for coluna in colunas:
                # USING ... AT TIME ZONE 'UTC' preserva o instante: o valor naive gravado pelo
                # utcnow antigo passa a ser o mesmo instante, agora com timezone explícito.
                await conn.execute(text(
                    f'ALTER TABLE "{tabela}" ALTER COLUMN "{coluna}" '
                    f'TYPE TIMESTAMPTZ USING "{coluna}" AT TIME ZONE \'UTC\''
                ))
                print(f'{tabela}.{coluna} -> timestamptz')

    print("Colunas de data/hora convertidas para timestamptz (valores interpretados como UTC).")


if __name__ == "__main__":
    asyncio.run(main())
