"""Verifica o isolamento multi-tenant via RLS e sessão tenant-aware.

Este script cria duas Empresas temporárias, grava dados em cada tenant usando a mesma
estratégia da API (`set_config('app.empresa_id', ...)`) e confirma que cada sessão só enxerga
os próprios registros de Condomínios, Usuários e Chamados.
"""

import asyncio
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
import sys

from sqlalchemy import delete, select, text

# Garante que `backend/` entre no sys.path quando o script é executado direto de `backend/scripts/`.
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.banco_dados import AsyncSessionLocal
from app.modelos.Chamados import Chamado, ChamadoFila, ChamadoPrioridade
from app.modelos.Condominio import Condominio
from app.modelos.Empresa import Empresa, EmpresaStatus
from app.modelos.Usuarios import Usuario, UsuarioFuncao


# Abre uma sessão já escopada ao tenant e limpa a variável ao final para não vazar no pool.
@asynccontextmanager
async def sessaoTenant(empresaID: uuid.UUID):
    async with AsyncSessionLocal() as session:
        await session.execute(
            text("SELECT set_config('app.empresa_id', :empresa_id, false)"),
            {"empresa_id": str(empresaID)},
        )
        try:
            yield session
        finally:
            await session.execute(text("RESET app.empresa_id"))
            await session.rollback()


# Gera nomes únicos para não colidir com dados já existentes no banco local.
def sufixoTemporario() -> str:
    return uuid.uuid4().hex[:8]


# Cria um bloco mínimo de dados dentro de um tenant: condomínio, cliente responsável e chamado.
async def criarDadosTenant(empresaID: uuid.UUID, rotulo: str) -> tuple[uuid.UUID, uuid.UUID, uuid.UUID]:
    async with sessaoTenant(empresaID) as session:
        condominio = Condominio(EmpresaID=empresaID, Nome=f"Condominio {rotulo}")
        session.add(condominio)
        await session.flush()

        usuario = Usuario(
            EmpresaID=empresaID,
            Nome=f"Cliente {rotulo}",
            Email=f"{rotulo.lower()}@teste.local",
            SenhaHash="hash-temporario",
            Funcao=UsuarioFuncao.Cliente,
            Condominio=condominio.Nome,
            CondominioID=condominio.ID,
        )
        session.add(usuario)
        await session.flush()

        chamado = Chamado(
            EmpresaID=empresaID,
            ClienteID=usuario.ID,
            Fila=ChamadoFila.Operacional,
            Categoria="Teste RLS",
            Resumo=f"Chamado {rotulo}",
            Prioridade=ChamadoPrioridade.Media,
        )
        session.add(chamado)
        await session.commit()
        return condominio.ID, usuario.ID, chamado.ID


# Descobre se o papel atual do banco ignora RLS no ambiente local.
async def papelAtualIgnoraRls() -> bool:
    async with AsyncSessionLocal() as session:
        resultado = await session.execute(
            text("select coalesce(rolsuper, false) or coalesce(rolbypassrls, false) from pg_roles where rolname = current_user")
        )
        return bool(resultado.scalar_one())


# Confirma a camada principal do app: mesmo com dados de dois tenants, as queries escopadas por
# EmpresaID retornam apenas o bloco pertencente à Empresa pedida.
async def validarFiltrosAplicacao(
    empresaID: uuid.UUID,
    esperadoCondominioID: uuid.UUID,
    esperadoUsuarioID: uuid.UUID,
    esperadoChamadoID: uuid.UUID,
) -> None:
    async with AsyncSessionLocal() as session:
        condominios = (
            await session.execute(
                select(Condominio.ID).where(Condominio.EmpresaID == empresaID).order_by(Condominio.Nome.asc())
            )
        ).scalars().all()
        usuarios = (
            await session.execute(
                select(Usuario.ID).where(Usuario.EmpresaID == empresaID).order_by(Usuario.Email.asc())
            )
        ).scalars().all()
        chamados = (
            await session.execute(
                select(Chamado.ID).where(Chamado.EmpresaID == empresaID).order_by(Chamado.Criacao.asc())
            )
        ).scalars().all()

    assert condominios == [esperadoCondominioID], f"Filtro por EmpresaID falhou em Condominios: {condominios}"
    assert usuarios == [esperadoUsuarioID], f"Filtro por EmpresaID falhou em Usuarios: {usuarios}"
    assert chamados == [esperadoChamadoID], f"Filtro por EmpresaID falhou em Chamados: {chamados}"


# Quando o papel do banco NÃO burla RLS, confirma também a trava secundária do Postgres.
async def validarVisibilidadeTenant(
    empresaID: uuid.UUID,
    esperadoCondominioID: uuid.UUID,
    esperadoUsuarioID: uuid.UUID,
    esperadoChamadoID: uuid.UUID,
) -> None:
    async with sessaoTenant(empresaID) as session:
        condominios = (
            await session.execute(select(Condominio.ID).order_by(Condominio.Nome.asc()))
        ).scalars().all()
        usuarios = (
            await session.execute(select(Usuario.ID).order_by(Usuario.Email.asc()))
        ).scalars().all()
        chamados = (
            await session.execute(select(Chamado.ID).order_by(Chamado.Criacao.asc()))
        ).scalars().all()

    assert condominios == [esperadoCondominioID], f"Tenant {empresaID} viu condominios indevidos: {condominios}"
    assert usuarios == [esperadoUsuarioID], f"Tenant {empresaID} viu usuarios indevidos: {usuarios}"
    assert chamados == [esperadoChamadoID], f"Tenant {empresaID} viu chamados indevidos: {chamados}"


# Remove os dados temporários no mesmo tenant que os criou para respeitar a RLS durante a limpeza.
async def limparDadosTenant(empresaID: uuid.UUID) -> None:
    async with sessaoTenant(empresaID) as session:
        await session.execute(delete(Chamado).where(Chamado.EmpresaID == empresaID))
        await session.execute(delete(Usuario).where(Usuario.EmpresaID == empresaID))
        await session.execute(delete(Condominio).where(Condominio.EmpresaID == empresaID))
        await session.commit()


# Fluxo principal: cria Empresas, semeia dados nos dois tenants, valida o isolamento e limpa tudo.
async def main() -> None:
    tag = sufixoTemporario()
    empresaAID: uuid.UUID | None = None
    empresaBID: uuid.UUID | None = None
    rlsDisponivel = not await papelAtualIgnoraRls()

    try:
        async with AsyncSessionLocal() as session:
            empresaA = Empresa(Nome=f"Empresa A {tag}", CNPJ=f"tmp-a-{tag}", Status=EmpresaStatus.Ativa)
            empresaB = Empresa(Nome=f"Empresa B {tag}", CNPJ=f"tmp-b-{tag}", Status=EmpresaStatus.Ativa)
            session.add_all([empresaA, empresaB])
            await session.commit()
            empresaAID = empresaA.ID
            empresaBID = empresaB.ID

        condominioAID, usuarioAID, chamadoAID = await criarDadosTenant(empresaAID, f"A-{tag}")
        condominioBID, usuarioBID, chamadoBID = await criarDadosTenant(empresaBID, f"B-{tag}")

        await validarFiltrosAplicacao(empresaAID, condominioAID, usuarioAID, chamadoAID)
        await validarFiltrosAplicacao(empresaBID, condominioBID, usuarioBID, chamadoBID)

        if rlsDisponivel:
            await validarVisibilidadeTenant(empresaAID, condominioAID, usuarioAID, chamadoAID)
            await validarVisibilidadeTenant(empresaBID, condominioBID, usuarioBID, chamadoBID)
            print("OK: filtros por EmpresaID e RLS validados para Condominios, Usuarios e Chamados.")
        else:
            print("OK: filtros por EmpresaID validados. RLS do Postgres foi pulada porque o papel local bypassa RLS.")
    finally:
        if empresaAID:
            await limparDadosTenant(empresaAID)
        if empresaBID:
            await limparDadosTenant(empresaBID)

        async with AsyncSessionLocal() as session:
            if empresaAID:
                await session.execute(delete(Empresa).where(Empresa.ID == empresaAID))
            if empresaBID:
                await session.execute(delete(Empresa).where(Empresa.ID == empresaBID))
            await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
