# Cookies de sessao do painel web (item S6 do plano).
#
# Por que cookie e nao localStorage: qualquer XSS no painel le o localStorage e rouba o token.
# Um cookie `HttpOnly` e invisivel para JavaScript, entao o mesmo XSS nao consegue exfiltra-lo
# (ele ainda pode FAZER requisicoes autenticadas do navegador da vitima — e para isso que existe
# a CSP do item S16 —, mas nao carrega o token para fora).
#
# O painel web fala com a API pelo proxy `/api/*` do Next, entao estes cookies sao *first-party*:
# o navegador os trata como pertencentes a origem do proprio painel. Por isso `SameSite=Lax` basta
# e o CORS nao precisa de `allow_credentials` (item S17).
#
# O app mobile NAO usa cookies: ele guarda o token no SecureStore e continua mandando
# `Authorization: Bearer`. As duas formas convivem — ver `obterTokenDaRequisicao` em rotas/Autenticacao.

import secrets

from fastapi import Response

from app.configuracoes import configuracoes

# Cookie da sessao: guarda o access token (JWT curto, item S15). HttpOnly — JavaScript nunca enxerga.
COOKIE_SESSAO = "sessao"

# Cookie do refresh token (item S15): guarda o valor opaco "{ID}.{segredo}" usado para trocar por
# um access token novo sem pedir senha de novo. HttpOnly pelo mesmo motivo do cookie de sessao;
# vive bem mais tempo (REFRESH_TOKEN_EXPIRE_DIAS) e só é lido/consumido em
# POST /autenticacao/atualizar e /autenticacao/logout.
COOKIE_REFRESH = "refresh"

# Cookie do token CSRF: legivel por JavaScript de proposito. O cliente le este valor e o repete
# no header `X-CSRF-Token`; o backend so aceita a requisicao se os dois baterem (double-submit).
# Um site atacante consegue FAZER o navegador enviar o cookie, mas nao consegue LER o valor dele
# (a same-origin policy o impede), entao nao sabe qual header mandar.
COOKIE_CSRF = "csrf_token"
HEADER_CSRF = "X-CSRF-Token"

# Cookie com a funcao do usuario: legivel, usado apenas para ROTEAMENTO na interface (o middleware
# do Next manda Superadmin para /plataforma). E forjavel pelo usuario, e isso e aceitavel: ele so
# muda qual tela o navegador tenta abrir. Toda autorizacao real acontece no backend, a partir do
# JWT assinado — forjar este cookie nao da acesso a dado nenhum.
COOKIE_FUNCAO = "funcao"


# Gera o valor do token CSRF. `token_urlsafe(32)` usa o gerador criptografico do SO — imprevisivel,
# que e a unica propriedade exigida de um token CSRF.
def gerarTokenCsrf() -> str:
    return secrets.token_urlsafe(32)


# Duracao dos cookies, casada com a validade real do JWT. Antes do S6 o cookie durava 7 dias
# enquanto o token expirava em 8h — o navegador seguia mandando um token morto, e o usuario via
# "sessao expirada" em vez de ser levado ao login.
def _maxAgeSegundos() -> int:
    return configuracoes.JWT_EXPIRE_MINUTES * 60


# Duracao do cookie de refresh (item S15) — bem maior que a do access token de proposito: e ele
# que sustenta a sessao "deslizante" enquanto o access token de 15min e renovado em segundo plano.
def _maxAgeRefreshSegundos() -> int:
    return configuracoes.REFRESH_TOKEN_EXPIRE_DIAS * 86400


# Escreve os cookies da sessao (access token, CSRF, funcao) na resposta. `path="/"` para valerem
# em toda a navegacao. Usada no login e em /autenticacao/atualizar (troca o access token sem
# mexer no refresh, que tem seu proprio cookie/ciclo de vida — ver definirCookieRefresh).
def definirCookiesSessao(resposta: Response, token: str, funcao: str) -> str:
    tokenCsrf = gerarTokenCsrf()
    comum = {
        "max_age": _maxAgeSegundos(),
        "path": "/",
        "secure": configuracoes.COOKIE_SECURE,
        "samesite": configuracoes.COOKIE_SAMESITE,
        "domain": configuracoes.COOKIE_DOMAIN or None,
    }
    resposta.set_cookie(COOKIE_SESSAO, token, httponly=True, **comum)
    # CSRF e funcao precisam ser lidos por JavaScript/middleware, entao nao sao HttpOnly.
    resposta.set_cookie(COOKIE_CSRF, tokenCsrf, httponly=False, **comum)
    resposta.set_cookie(COOKIE_FUNCAO, funcao, httponly=False, **comum)
    return tokenCsrf


# Escreve/renova o cookie do refresh token (item S15) — separado de definirCookiesSessao porque
# tem duracao diferente e e escrito tanto no login (familia nova) quanto em cada rotacao bem-
# sucedida (proximo elo da familia).
def definirCookieRefresh(resposta: Response, valorRefresh: str) -> None:
    resposta.set_cookie(
        COOKIE_REFRESH,
        valorRefresh,
        httponly=True,
        max_age=_maxAgeRefreshSegundos(),
        path="/",
        secure=configuracoes.COOKIE_SECURE,
        samesite=configuracoes.COOKIE_SAMESITE,
        domain=configuracoes.COOKIE_DOMAIN or None,
    )


# Remove os cookies no logout. Os atributos (path/domain/secure/samesite) precisam bater com os
# usados na criacao — senao o navegador entende que e outro cookie e o original sobrevive.
def limparCookiesSessao(resposta: Response) -> None:
    for nome in (COOKIE_SESSAO, COOKIE_CSRF, COOKIE_FUNCAO, COOKIE_REFRESH):
        resposta.delete_cookie(
            nome,
            path="/",
            domain=configuracoes.COOKIE_DOMAIN or None,
            secure=configuracoes.COOKIE_SECURE,
            samesite=configuracoes.COOKIE_SAMESITE,
        )
