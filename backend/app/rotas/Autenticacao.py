# Rotas de autenticação e utilitários de segurança JWT
# Responsável por: login, geração de token e validação do usuário atual em rotas protegidas

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
import jwt
from jwt import PyJWTError
from datetime import datetime, timedelta, timezone
from app.banco_dados import obterBancoDados
from app.tempo import agoraUtc
from app.modelos.Usuarios import Usuario
from app.modelos.Empresa import Empresa, EmpresaStatus
from app.configuracoes import configuracoes
from app.servicos.hasher import pwd
from app.servicos.seguranca import aplicarRateLimitAutenticacao
from app.servicos.sessao import COOKIE_REFRESH, COOKIE_SESSAO, definirCookieRefresh, definirCookiesSessao, limparCookiesSessao
from app.servicos.revogacao import registrarRevogacao, tokenRevogado
from app.servicos.refresh import RefreshInvalido, criarFamiliaRefresh, obterFamiliaPorValor, revogarFamilia, rotacionar
import uuid

roteador = APIRouter(prefix="/autenticacao", tags=["Autenticacao"])

# Hash dummy usado quando o email nao existe, reduzindo diferenca de timing entre usuario existente
# e inexistente no login. O valor representa uma senha aleatoria sem utilidade operacional.
HASH_DUMMY_LOGIN = pwd.hash("senha-dummy-para-uniformizar-tempo-de-login")

# Informa ao FastAPI onde está o endpoint de login para o fluxo OAuth2 (exibido no Swagger).
# `auto_error=False`: sem o header Authorization, devolve None em vez de lançar 401 — porque o
# painel web autentica por cookie, e quem decide se há credencial é `obterTokenDaRequisicao`.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/autenticacao/login", auto_error=False)


# Extrai o token da requisição, aceitando as DUAS formas de sessão que o produto usa (item S6):
# o cookie `HttpOnly` do painel web e o header `Authorization: Bearer` do app mobile (SecureStore).
# O header tem precedência: se o cliente se identificou explicitamente, é essa credencial que vale.
async def obterTokenDaRequisicao(
    request: Request,
    tokenDoHeader: str | None = Depends(oauth2_scheme),
) -> str:
    token = tokenDoHeader or request.cookies.get(COOKIE_SESSAO)
    if not token:
        raise HTTPException(status_code=401, detail="Não autenticado")
    return token


# Mesma extração acima, mas sem exigir credencial — usada no logout, que precisa aceitar chamadas
# sem sessão (nada a revogar) sem responder 401 por isso.
async def obterTokenOpcionalDaRequisicao(
    request: Request,
    tokenDoHeader: str | None = Depends(oauth2_scheme),
) -> str | None:
    return tokenDoHeader or request.cookies.get(COOKIE_SESSAO)


# Gera um token JWT com o ID, função e tenant (Empresa) do usuário, válido pelo tempo configurado
# em JWT_EXPIRE_MINUTES. O empresa_id viaja no token para que o front nunca precise informar o
# tenant (regra da Fase 0.7 — "tenant vem do token").
def criarToken(usuarioID: str, funcao: str, empresaID: str) -> str:
    # agoraUtc (timezone-aware) no lugar do datetime.utcnow deprecado — o PyJWT converte para epoch
    agora = agoraUtc()
    expiracao = agora + timedelta(minutes=configuracoes.JWT_EXPIRE_MINUTES)
    payload = {
        "sub": usuarioID,  # subject: identificador único do usuário
        "funcao": funcao,
        "empresa_id": empresaID,
        "iat": agora,                          # quando o token foi emitido
        "exp": expiracao,
        "iss": configuracoes.JWT_ISSUER,       # quem emitiu (item B6)
        "aud": configuracoes.JWT_AUDIENCE,     # para quem o token vale
        "jti": uuid.uuid4().hex,               # ID único do token — chave da revogação (item S14)
    }
    return jwt.encode(payload, configuracoes.JWT_SECRET, algorithm=configuracoes.JWT_ALGORITHM)

# Decodifica e valida um JWT: assinatura, expiração e as claims `iss`/`aud` (item B6) — um token
# emitido para outro público ou por outro emissor já é rejeitado aqui, antes de checar a denylist.
# Centraliza os parâmetros do decode para as duas dependências abaixo não divergirem.
def _decodificarToken(token: str) -> dict:
    return jwt.decode(
        token,
        configuracoes.JWT_SECRET,
        algorithms=[configuracoes.JWT_ALGORITHM],
        issuer=configuracoes.JWT_ISSUER,
        audience=configuracoes.JWT_AUDIENCE,
    )


# Dependência leve — decodifica o token e devolve o payload cru (jti/exp), sem consultar o banco.
# Usada por rotas que precisam revogar a PRÓPRIA sessão atual (item S14, ex.: troca de senha) além
# do usuário autenticado — decodifica de novo (barato, sem I/O) em vez de mudar a assinatura de
# `obterUsuarioAtual` e arriscar quebrar as dezenas de rotas que já dependem dela.
async def obterPayloadTokenAtual(token: str = Depends(obterTokenDaRequisicao)) -> dict:
    try:
        return _decodificarToken(token)
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")


# Dependência injetável — decodifica o token da requisição e retorna o usuário autenticado
# Usada em todas as rotas protegidas com Depends(obterUsuarioAtual)
async def obterUsuarioAtual(
    token: str = Depends(obterTokenDaRequisicao),
    db: AsyncSession = Depends(obterBancoDados)
):
    try:
        payload = _decodificarToken(token)
        usuarioID = payload.get("sub")
        if not usuarioID:
            raise HTTPException(status_code=401, detail="Token inválido")
        usuarioUUID = uuid.UUID(usuarioID)
    except (PyJWTError, ValueError):
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    # Denylist do item S14: um token só passa daqui se o seu `jti` não tiver sido revogado no logout.
    if await tokenRevogado(db, payload.get("jti")):
        raise HTTPException(status_code=401, detail="Sessão encerrada")

    resultado = await db.execute(select(Usuario).where(Usuario.ID == usuarioUUID))
    usuario = resultado.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    resultadoEmpresa = await db.execute(select(Empresa).where(Empresa.ID == usuario.EmpresaID))
    empresa = resultadoEmpresa.scalar_one_or_none()
    if not empresa or empresa.Status == EmpresaStatus.Suspensa:
        raise HTTPException(status_code=403, detail="Empresa suspensa")
    return usuario

# Dependência leve — extrai só o tenant (EmpresaID) do token, sem carregar o Usuario inteiro do banco.
# Existe separada de obterUsuarioAtual para rotas/serviços que só precisam do escopo do tenant
# (ex.: filtros de query), evitando um SELECT extra quando o usuário completo não é necessário.
# Também checa a denylist (S14): a checagem é barata (busca por chave primária) e assim a
# revogação vale mesmo em rotas que só dependem do tenant, sem exigir o SELECT completo do Usuario.
async def obterTenantAtual(
    token: str = Depends(obterTokenDaRequisicao),
    db: AsyncSession = Depends(obterBancoDados),
) -> uuid.UUID:
    try:
        payload = _decodificarToken(token)
        empresaID = payload.get("empresa_id")
        if not empresaID:
            raise HTTPException(status_code=401, detail="Token sem tenant")
        empresaUUID = uuid.UUID(empresaID)
    except (PyJWTError, ValueError):
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    if await tokenRevogado(db, payload.get("jti")):
        raise HTTPException(status_code=401, detail="Sessão encerrada")

    return empresaUUID

# Dependência que entrega uma sessão de banco já escopada ao tenant via RLS (trava secundária,
# ver backend/app/rls.sql): define a variável de sessão Postgres `app.empresa_id` a partir do
# token ANTES de qualquer query da rota rodar. Rotas que leem/gravam dados sensíveis a tenant devem
# preferir esta dependência a `obterBancoDados` puro sempre que praticável.
async def obterBancoDadosComTenant(
    empresaID: uuid.UUID = Depends(obterTenantAtual),
    db: AsyncSession = Depends(obterBancoDados),
):
    # Usa escopo de sessão (não transação-local) para que o tenant continue aplicado mesmo após
    # commits internos da rota. No finally, o valor é limpo para não vazar para a próxima
    # requisição quando a conexão voltar ao pool.
    await db.execute(
        text("SELECT set_config('app.empresa_id', :empresa_id, false)"),
        {"empresa_id": str(empresaID)},
    )
    try:
        yield db
    finally:
        await db.execute(text("RESET app.empresa_id"))

# POST /autenticacao/login — recebe email e senha, retorna o token JWT e dados básicos do usuário.
# Além do corpo, emite os cookies de sessão (S6): o painel web usa os cookies e ignora o
# `token_acesso` do corpo; o app mobile faz o inverso (guarda o token no SecureStore e descarta
# os cookies). Uma rota só, servindo os dois clientes.
@roteador.post("/login")
async def login(
    request: Request,
    resposta: Response,
    formulario: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(obterBancoDados)
):
    aplicarRateLimitAutenticacao("login", request, formulario.username)

    resultado = await db.execute(select(Usuario).where(Usuario.Email == formulario.username))
    usuario = resultado.scalar_one_or_none()

    # Usa hash real ou dummy para reduzir diferenca de timing entre email existente e inexistente.
    hashParaVerificar = usuario.SenhaHash if usuario else HASH_DUMMY_LOGIN
    senhaValida = pwd.verify(formulario.password, hashParaVerificar)

    # Rejeita com mensagem uniforme se o usuario nao existe ou a senha nao confere.
    if not usuario or not senhaValida:
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")

    # Fase 4: usuario desativado (Usuario.Ativo=False) nao loga - "remover" da equipe e sempre
    # desativacao, nunca exclusao, mas o acesso precisa parar de valer a partir dai.
    if not usuario.Ativo:
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")

    # Nome da Empresa vai junto na resposta do login (não no JWT) só para exibição na UI
    # (ex.: "Admin · Cefram" no cabeçalho do painel) — o backend nunca confia nesse campo depois.
    resultadoEmpresa = await db.execute(select(Empresa).where(Empresa.ID == usuario.EmpresaID))
    empresa = resultadoEmpresa.scalar_one_or_none()
    if not empresa or empresa.Status == EmpresaStatus.Suspensa:
        raise HTTPException(status_code=403, detail="Empresa suspensa")

    token = criarToken(str(usuario.ID), usuario.Funcao.value, str(usuario.EmpresaID))
    # Abre uma família de refresh nova para esta sessão (item S15) — é o que sustenta o usuário
    # "logado" por dias sem repetir a senha, enquanto o access token acima dura só 15min.
    valorRefresh = await criarFamiliaRefresh(db, usuario.ID, usuario.EmpresaID)

    # Cookies da sessão web: `sessao` (access, HttpOnly), `csrf_token`, `funcao` e `refresh`.
    definirCookiesSessao(resposta, token, usuario.Funcao.value)
    definirCookieRefresh(resposta, valorRefresh)

    return {
        "token_acesso": token,
        "tipo_token": "bearer",
        # O app mobile não tem cookies: guarda este valor no SecureStore e o reenvia no corpo de
        # POST /autenticacao/atualizar. O painel web ignora este campo (usa o cookie `refresh`).
        "refresh_token": valorRefresh,
        "funcao": usuario.Funcao.value,
        "nome": usuario.Nome,
        "empresa_id": str(usuario.EmpresaID),
        "empresa_nome": empresa.Nome if empresa else None,
    }


# Lê o refresh token de uma requisição sem exigi-lo: cookie `refresh` (web) ou campo
# `refresh_token` no corpo JSON (mobile, sem cookies). Corpo ausente/inválido é tratado como
# "não enviou" — usado por /logout e /atualizar, que não podem 422 por causa de um corpo vazio.
async def _obterRefreshDaRequisicao(request: Request) -> str | None:
    try:
        corpo = await request.json()
    except Exception:
        corpo = {}
    return (corpo or {}).get("refresh_token") or request.cookies.get(COOKIE_REFRESH)


# POST /autenticacao/logout — encerra a sessão de verdade (itens S14/S15): além de apagar os
# cookies do cliente, registra o `jti` do access token na denylist e revoga a FAMÍLIA inteira do
# refresh token, então nem uma cópia do access token nem do refresh (roubados antes do logout)
# continuam funcionando — não precisa esperar a expiração de nenhum dos dois.
#
# Não exige autenticação: chamar logout sem sessão simplesmente não faz nada (não há nada a
# revogar). Exigir um token válido só criaria um jeito de o usuário ficar preso numa sessão
# expirada, sem conseguir limpar os cookies. Tokens já expirados/inválidos são ignorados de
# propósito — já seriam rejeitados pela expiração de qualquer forma.
@roteador.post("/logout")
async def logout(
    request: Request,
    resposta: Response,
    token: str | None = Depends(obterTokenOpcionalDaRequisicao),
    db: AsyncSession = Depends(obterBancoDados),
):
    if token:
        try:
            payload = _decodificarToken(token)
            jti = payload.get("jti")
            usuarioID = payload.get("sub")
            empresaID = payload.get("empresa_id")
            expiracao = payload.get("exp")
            if jti and usuarioID and empresaID and expiracao:
                await registrarRevogacao(
                    db,
                    uuid.UUID(empresaID),
                    uuid.UUID(usuarioID),
                    jti,
                    datetime.fromtimestamp(expiracao, tz=timezone.utc),
                )
        except (PyJWTError, ValueError):
            pass  # token já inválido/expirado — nada de novo a revogar

    valorRefresh = await _obterRefreshDaRequisicao(request)
    if valorRefresh:
        familiaID = await obterFamiliaPorValor(db, valorRefresh)
        if familiaID:
            await revogarFamilia(db, familiaID)

    limparCookiesSessao(resposta)
    return {"mensagem": "Sessão encerrada"}


# POST /autenticacao/atualizar — troca um refresh token válido por um access token novo (item
# S15), sem pedir senha de novo. Roda a rotação (servicos/refresh.rotacionar): o token recebido é
# consumido e um novo nasce na mesma família; reuso de um token já consumido derruba a família
# inteira (sinal de furto). Reaplica as mesmas checagens de Empresa suspensa do login/
# obterUsuarioAtual — um refresh não pode reviver o acesso de uma Empresa suspensa entretanto.
@roteador.post("/atualizar")
async def atualizarToken(
    request: Request,
    resposta: Response,
    db: AsyncSession = Depends(obterBancoDados),
):
    valorRefresh = await _obterRefreshDaRequisicao(request)
    if not valorRefresh:
        raise HTTPException(status_code=401, detail="Refresh token ausente")

    try:
        novoValorRefresh, usuarioID, empresaID = await rotacionar(db, valorRefresh)
    except RefreshInvalido:
        limparCookiesSessao(resposta)
        raise HTTPException(status_code=401, detail="Sessão expirada. Faça login novamente.")

    resultado = await db.execute(select(Usuario).where(Usuario.ID == usuarioID))
    usuario = resultado.scalar_one_or_none()
    resultadoEmpresa = await db.execute(select(Empresa).where(Empresa.ID == empresaID))
    empresa = resultadoEmpresa.scalar_one_or_none()
    if not usuario or not empresa or empresa.Status == EmpresaStatus.Suspensa:
        limparCookiesSessao(resposta)
        raise HTTPException(status_code=403, detail="Empresa suspensa")

    novoToken = criarToken(str(usuario.ID), usuario.Funcao.value, str(usuario.EmpresaID))
    definirCookiesSessao(resposta, novoToken, usuario.Funcao.value)
    definirCookieRefresh(resposta, novoValorRefresh)

    return {
        "token_acesso": novoToken,
        "tipo_token": "bearer",
        "refresh_token": novoValorRefresh,
        "funcao": usuario.Funcao.value,
        "nome": usuario.Nome,
        "empresa_id": str(usuario.EmpresaID),
        "empresa_nome": empresa.Nome if empresa else None,
    }
