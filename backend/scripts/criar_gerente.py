# Script de bootstrap para criar o PRIMEIRO usuário Gerente do sistema.
#
# Por que existe: por segurança (item C6), o cadastro público (POST /usuarios/) sempre cria
# um usuário Cliente, e a criação de perfis privilegiados (POST /usuarios/equipe) exige um
# Gerente já autenticado. Logo, o primeiro Gerente precisa ser criado fora da API, por aqui.
#
# Como usar (a partir da pasta backend/, com o .env configurado e o Postgres no ar):
#   python scripts/criar_gerente.py "Nome do Gestor" gestor@exemplo.com SenhaForte123
#
# Depois do primeiro Gerente, todos os demais usuários da equipe podem ser criados pela API.

import os
import sys
import asyncio

# Garante que a raiz do backend (pasta-pai de scripts/) esteja no sys.path.
# Sem isso, rodar `python scripts/criar_gerente.py` não encontraria o pacote `app`,
# pois o Python coloca a pasta do script no path, e não a raiz do backend.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pwdlib import PasswordHash

from app.banco_dados import engine, Base, AsyncSessionLocal
from app.modelos.Usuarios import Usuario, UsuarioFuncao
import app.modelos  # importa todos os modelos para que o create_all conheça todas as tabelas

# Hasher de senha (mesmo algoritmo argon2 usado nas rotas de autenticação)
pwd = PasswordHash.recommended()

# Validação dos argumentos de linha de comando — evita senha fixa no código-fonte
if len(sys.argv) != 4:
    print('Uso: python scripts/criar_gerente.py "<Nome>" <Email> <Senha>')
    sys.exit(1)

nome, email, senha = sys.argv[1], sys.argv[2], sys.argv[3]


async def main():
    # Garante que as tabelas existem (idempotente — não recria o que já existe)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Cria o usuário com função Gerente e senha armazenada apenas como hash
        gerente = Usuario(
            Nome=nome,
            Email=email,
            SenhaHash=pwd.hash(senha),
            Funcao=UsuarioFuncao.Gerente,
        )
        db.add(gerente)
        await db.commit()

    print(f"Gerente criado com sucesso: {email}")


# Executa a rotina assíncrona quando o script é chamado diretamente
if __name__ == "__main__":
    asyncio.run(main())
