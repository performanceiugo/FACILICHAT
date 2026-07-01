# Script utilitário — aplica as políticas de Row-Level Security (app/rls.sql) no Postgres.
#
# Por que existe: RLS não é criado por Base.metadata.create_all() (isso só cria tabelas/colunas);
# políticas são DDL específico do Postgres, aplicado uma vez fora do ciclo normal do SQLAlchemy.
# Idempotente — usa DROP POLICY IF EXISTS, pode rodar de novo sem erro.
#
# Como usar (a partir da pasta backend/, com o .env configurado e o Postgres no ar,
# DEPOIS que as tabelas já existem — rode create_all/suba a API pelo menos uma vez antes):
#   python scripts/aplicar_rls.py

import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.banco_dados import engine


async def main():
    caminho_sql = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "rls.sql")
    with open(caminho_sql, "r", encoding="utf-8") as arquivo:
        script_sql = arquivo.read()

    async with engine.begin() as conn:
        # Cada comando é executado separadamente — asyncpg não aceita múltiplos statements numa só chamada
        for comando in [c.strip() for c in script_sql.split(";") if c.strip() and not c.strip().startswith("--")]:
            await conn.execute(text(comando))

    print("Políticas de RLS aplicadas com sucesso.")


if __name__ == "__main__":
    asyncio.run(main())
