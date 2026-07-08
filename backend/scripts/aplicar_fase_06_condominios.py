# Aplica a mudanca incremental da Fase 0.6: cria a entidade Condominio e vincula Usuarios por
# CondominioID, mantendo o campo textual legado para compatibilidade.
#
# Como usar a partir de backend/:
#   python scripts/aplicar_fase_06_condominios.py

import os
import sys
import asyncio
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.banco_dados import engine


async def main():
    async with engine.begin() as conn:
        # Cria a nova tabela sem assumir Alembic/migrations neste momento do projeto.
        await conn.execute(
            text(
                '''
                CREATE TABLE IF NOT EXISTS "Condominios" (
                    "ID" UUID PRIMARY KEY,
                    "EmpresaID" UUID NOT NULL REFERENCES "Empresas"("ID"),
                    "Nome" VARCHAR(150) NOT NULL,
                    "Criacao" TIMESTAMP NULL
                )
                '''
            )
        )
        # Adiciona a FK estruturada em Usuarios e um indice para consultas por condominio.
        await conn.execute(text('ALTER TABLE "Usuarios" ADD COLUMN IF NOT EXISTS "CondominioID" UUID'))
        await conn.execute(
            text(
                '''
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM pg_constraint
                        WHERE conname = 'fk_usuarios_condominioid'
                    ) THEN
                        ALTER TABLE "Usuarios"
                        ADD CONSTRAINT fk_usuarios_condominioid
                        FOREIGN KEY ("CondominioID") REFERENCES "Condominios"("ID");
                    END IF;
                END $$;
                '''
            )
        )
        await conn.execute(text('CREATE INDEX IF NOT EXISTS "ix_Usuarios_CondominioID" ON "Usuarios" ("CondominioID")'))
        # Impede duplicatas casuais do mesmo Condominio por variacao de caixa no nome.
        await conn.execute(
            text(
                '''
                CREATE UNIQUE INDEX IF NOT EXISTS "ux_Condominios_EmpresaID_NomeLower"
                ON "Condominios" ("EmpresaID", LOWER("Nome"))
                '''
            )
        )

        # Faz backfill dos textos legados para registros reais de Condominio por tenant.
        usuarios = (
            await conn.execute(
                text(
                    '''
                    SELECT "ID", "EmpresaID", "Condominio"
                    FROM "Usuarios"
                    WHERE "Condominio" IS NOT NULL
                      AND BTRIM("Condominio") <> ''
                    '''
                )
            )
        ).mappings().all()

        mapa_condominios: dict[tuple[str, str], uuid.UUID] = {}
        for usuario in usuarios:
            nome = usuario["Condominio"].strip()
            chave = (str(usuario["EmpresaID"]), nome.casefold())

            if chave not in mapa_condominios:
                existente = (
                    await conn.execute(
                        text(
                            '''
                            SELECT "ID"
                            FROM "Condominios"
                            WHERE "EmpresaID" = :empresa_id
                              AND "Nome" = :nome
                            '''
                        ),
                        {"empresa_id": usuario["EmpresaID"], "nome": nome},
                    )
                ).scalar_one_or_none()

                if existente is None:
                    existente = uuid.uuid4()
                    await conn.execute(
                        text(
                            '''
                            INSERT INTO "Condominios" ("ID", "EmpresaID", "Nome", "Criacao")
                            VALUES (:id, :empresa_id, :nome, NOW())
                            '''
                        ),
                        {"id": existente, "empresa_id": usuario["EmpresaID"], "nome": nome},
                    )

                mapa_condominios[chave] = existente

            await conn.execute(
                text(
                    '''
                    UPDATE "Usuarios"
                    SET "CondominioID" = :condominio_id
                    WHERE "ID" = :usuario_id
                    '''
                ),
                {
                    "condominio_id": mapa_condominios[chave],
                    "usuario_id": usuario["ID"],
                },
            )

    print("Entidade Condominio e vinculo CondominioID aplicados com sucesso.")


if __name__ == "__main__":
    asyncio.run(main())
