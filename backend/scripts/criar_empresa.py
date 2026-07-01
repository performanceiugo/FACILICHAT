# Script de bootstrap para criar a PRIMEIRA Empresa (tenant) e o primeiro Gestor dela.
#
# Por que existe: substitui o antigo criar_gerente.py (Fase 0.5/C6) agora que o sistema é
# multi-tenant (Fase 0.7) — todo Usuario precisa de uma EmpresaID, então não basta mais criar um
# usuário privilegiado solto: é preciso criar a Empresa junto, numa única transação, e só então o
# 1º Gestor daquela Empresa (que poderá, pela API, criar o resto da equipe via POST /usuarios/equipe).
#
# Como usar (a partir da pasta backend/, com o .env configurado e o Postgres no ar):
#   python scripts/criar_empresa.py "Nome da Empresa" 12.345.678/0001-90 "Nome do Gestor" gestor@exemplo.com SenhaForte123

import os
import sys
import asyncio

# Garante que a raiz do backend (pasta-pai de scripts/) esteja no sys.path — ver criar_gerente.py (removido).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pwdlib import PasswordHash

from app.banco_dados import engine, Base, AsyncSessionLocal
from app.modelos.Empresa import Empresa
from app.modelos.Usuarios import Usuario, UsuarioFuncao
import app.modelos  # importa todos os modelos para que o create_all conheça todas as tabelas

pwd = PasswordHash.recommended()

if len(sys.argv) != 6:
    print(
        'Uso: python scripts/criar_empresa.py "<Nome da Empresa>" <CNPJ> "<Nome do Gestor>" <Email> <Senha>'
    )
    sys.exit(1)

nomeEmpresa, cnpj, nomeGestor, email, senha = sys.argv[1:6]


async def main():
    # Garante que as tabelas existem (idempotente — não recria o que já existe)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Cria a Empresa (tenant) e o primeiro Gestor numa única transação — se o Gestor falhar
        # ao ser criado, a Empresa também não é persistida (evita tenant órfão sem nenhum usuário).
        empresa = Empresa(Nome=nomeEmpresa, CNPJ=cnpj)
        db.add(empresa)
        await db.flush()  # garante empresa.ID preenchido antes de criar o Usuario que referencia

        gestor = Usuario(
            EmpresaID=empresa.ID,
            Nome=nomeGestor,
            Email=email,
            SenhaHash=pwd.hash(senha),
            Funcao=UsuarioFuncao.Gestor,
        )
        db.add(gestor)
        await db.commit()

    print(f"Empresa criada: {nomeEmpresa} ({cnpj})")
    print(f"Gestor criado com sucesso: {email}")


if __name__ == "__main__":
    asyncio.run(main())
