# Aplica a mudança incremental da Fase 0.6: coluna GrupoOrigemID em Chamados.
# Idempotente para bancos de dev já existentes, enquanto Alembic não está ativo no projeto.
#
# Como usar a partir de backend/:
#   python scripts/aplicar_fase_06_tickets_irmaos.py

import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.banco_dados import engine


async def main():
    comandos = [
        'ALTER TABLE "Chamados" ADD COLUMN IF NOT EXISTS "GrupoOrigemID" UUID',
        'CREATE INDEX IF NOT EXISTS "ix_Chamados_GrupoOrigemID" ON "Chamados" ("GrupoOrigemID")',
    ]
    async with engine.begin() as conn:
        for comando in comandos:
            await conn.execute(text(comando))

    print("Coluna GrupoOrigemID aplicada em Chamados.")


if __name__ == "__main__":
    asyncio.run(main())
