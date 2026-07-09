# Protecao CSRF do backend (item S6 do plano).
#
# O problema que isto resolve: assim que a sessao passa a viajar em cookie, o navegador anexa esse
# cookie AUTOMATICAMENTE em requisicoes disparadas por qualquer site. Um formulario escondido em
# `site-malicioso.com` poderia fazer o navegador da vitima chamar a nossa API ja autenticado.
#
# `SameSite=Lax` sozinho NAO basta (recomendacao explicita do OWASP CSRF Cheat Sheet): ele nao
# cobre subdominios comprometidos, alguns navegadores antigos o ignoram, e um bug de navegador
# derruba a unica camada. Por isso combinamos duas defesas independentes:
#
# 1. Validacao de `Origin`/`Referer` — se o navegador disse de onde veio, o valor precisa estar na
#    lista de origens confiaveis. Cobre tambem o *login CSRF* (atacante logar a vitima na conta
#    dele), que o double-submit nao cobre, porque no login ainda nao existe sessao.
# 2. Double-submit token — o cliente le o cookie `csrf_token` e repete o valor no header
#    `X-CSRF-Token`. Um site atacante consegue fazer o navegador ENVIAR o cookie, mas a
#    same-origin policy o impede de LER o valor, entao ele nao sabe qual header mandar.
#
# O app mobile autentica por `Authorization: Bearer` e NAO participa disso: um header precisa ser
# adicionado explicitamente por codigo, nunca e anexado sozinho pelo navegador. Sem credencial
# ambiente, nao ha CSRF — por isso requisicoes com Bearer pulam a checagem de token.

import secrets

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.configuracoes import configuracoes
from app.servicos.sessao import COOKIE_CSRF, COOKIE_SESSAO, HEADER_CSRF

# Metodos que alteram estado. GET/HEAD/OPTIONS sao seguros por definicao (RFC 9110) e ficam de fora:
# barrar preflight (OPTIONS) quebraria o CORS, e barrar GET quebraria a navegacao.
METODOS_QUE_MUDAM_ESTADO = {"POST", "PUT", "PATCH", "DELETE"}

# Rotas isentas do double-submit (mas NAO da validacao de Origin/Referer).
#
# `/autenticacao/logout`: se o cookie `csrf_token` sumir (expirou antes do de sessao, foi limpo
# pelo navegador), exigir o token deixaria o usuario preso — sem conseguir apagar a propria sessao.
# O risco aceito e um atacante deslogar a vitima: irritante, nao perigoso. A validacao de origem
# continua valendo, entao nem isso e trivial.
ROTAS_SEM_DOUBLE_SUBMIT = {"/autenticacao/logout"}


# Extrai a origem (`esquema://host:porta`) do header `Referer`, para quando `Origin` nao vier.
def _origemDoReferer(referer: str) -> str | None:
    from urllib.parse import urlparse

    try:
        partes = urlparse(referer)
    except ValueError:
        return None
    if not partes.scheme or not partes.netloc:
        return None
    return f"{partes.scheme}://{partes.netloc}"


class CsrfMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method not in METODOS_QUE_MUDAM_ESTADO:
            return await call_next(request)

        origensConfiaveis = configuracoes.cors_origins_lista

        # --- Defesa 1: de onde a requisicao diz que veio ---------------------------------------
        # `Origin` e enviado pelo navegador em toda requisicao que muda estado e NAO pode ser
        # forjado por JavaScript. Quando ausente (curl, app mobile, server-to-server), nao ha
        # navegador para ser enganado — entao a ausencia nao e motivo para bloquear.
        origem = request.headers.get("origin")
        if origem is None:
            referer = request.headers.get("referer")
            origem = _origemDoReferer(referer) if referer else None

        if origem is not None and origem not in origensConfiaveis:
            return JSONResponse(status_code=403, content={"detail": "Origem não autorizada"})

        # --- Defesa 2: double-submit, so para quem autentica por cookie -------------------------
        # Bearer nao e credencial ambiente: o navegador nunca o anexa sozinho. Se a requisicao traz
        # `Authorization`, nao ha superficie de CSRF e o token nao e exigido.
        temCookieSessao = COOKIE_SESSAO in request.cookies
        usaBearer = "authorization" in request.headers
        isenta = request.url.path in ROTAS_SEM_DOUBLE_SUBMIT
        if not temCookieSessao or usaBearer or isenta:
            return await call_next(request)

        cookieCsrf = request.cookies.get(COOKIE_CSRF)
        headerCsrf = request.headers.get(HEADER_CSRF)
        # `compare_digest` compara em tempo constante: um `==` comum vazaria, pelo tempo de resposta,
        # quantos caracteres iniciais do token o atacante acertou.
        if not cookieCsrf or not headerCsrf or not secrets.compare_digest(cookieCsrf, headerCsrf):
            return JSONResponse(status_code=403, content={"detail": "Token CSRF ausente ou inválido"})

        return await call_next(request)
