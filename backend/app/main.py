# Ponto de entrada da aplicação FaciliChat
# Inicializa o FastAPI, cria as tabelas no banco de dados e registra as rotas

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.banco_dados import engine, Base
from app.configuracoes import configuracoes
from app import modelos  # importação necessária para que o SQLAlchemy reconheça os modelos antes do create_all
from app.rotas import Autenticacao, Usuarios, Chamados, Plataforma, Relatorios
from app.servicos.csrf import CsrfMiddleware


# Substitui o `@app.on_event("startup")` deprecado (item B6). `lifespan` roda o código antes do
# `yield` na subida e o que viesse depois do `yield` no encerramento — hoje não há nada a limpar.
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Banco de dados conectado!")
    yield


# Instância principal da aplicação — título e versão aparecem no Swagger (/docs).
# Docs configuráveis por ambiente (item S8): com API_DOCS_HABILITADO=false, os três parâmetros
# viram None e o FastAPI nem registra as rotas de /docs, /redoc e /openapi.json (não é só uma
# UI escondida — o schema deixa de ser gerado/servido).
_docsHabilitados = configuracoes.API_DOCS_HABILITADO
app = FastAPI(
    title="FaciliChat",
    description="Plataforma de atendimento para gestão de condomínios",
    version="0.1.0",
    docs_url="/docs" if _docsHabilitados else None,
    redoc_url="/redoc" if _docsHabilitados else None,
    openapi_url="/openapi.json" if _docsHabilitados else None,
    lifespan=lifespan,
)

# Métodos HTTP realmente expostos pela API (rotas em app/rotas/). Listar explicitamente, em vez de
# "*", evita anunciar ao navegador verbos que não existem (PUT, DELETE, HEAD). Ao criar uma rota com
# um verbo novo, ele precisa ser adicionado aqui — senão o preflight do navegador reprova a chamada.
CORS_METODOS_PERMITIDOS = ["GET", "POST", "PATCH", "OPTIONS"]

# Headers que os frontends enviam. `Content-Type` já entra pela safelist do CORS, mas fica explícito
# para o preflight de JSON. Com "*", o Starlette devolveria de volta QUALQUER header pedido pelo
# cliente (ele espelha o `Access-Control-Request-Headers`), o que é uma permissão em branco.
CORS_HEADERS_PERMITIDOS = ["Authorization", "Content-Type"]

# Proteção CSRF (item S6) — obrigatória a partir do momento em que a sessão do painel viaja em
# cookie, porque o navegador anexa cookies sozinho em requisições vindas de qualquer site.
# Registrado ANTES do CORS de propósito: no FastAPI, o último middleware adicionado é o mais
# externo, então o CORS envolve o CSRF. Assim o preflight (OPTIONS) é respondido pelo CORS sem
# passar pelo CSRF, e um 403 do CSRF ainda sai com os headers de CORS — sem isso o navegador
# esconderia o erro real do painel atrás de uma mensagem genérica de CORS.
app.add_middleware(CsrfMiddleware)

# CORS — libera os frontends (web/mobile) configurados a chamar a API pelo navegador.
# Origens explícitas (nunca "*") vindas das configurações/.env.
#
# `allow_credentials=False` (item S17): hoje a autenticação é por header `Authorization: Bearer`,
# e nenhum cliente envia cookies (`credentials: 'include'`). Manter o flag ligado só anunciava um
# poder que ninguém usa. Quando o S6 migrar a sessão do web para cookie `HttpOnly`, este flag volta
# a `True` — mas **somente junto** da proteção CSRF (token imprevisível + validação de Origin/Referer),
# porque `SameSite` sozinho não basta. A especificação também proíbe "*" em `allow_methods`,
# `allow_headers` e `allow_origins` em requisições credenciadas, então as listas explícitas abaixo
# já deixam a configuração pronta para essa virada.
app.add_middleware(
    CORSMiddleware,
    allow_origins=configuracoes.cors_origins_lista,
    allow_credentials=False,
    allow_methods=CORS_METODOS_PERMITIDOS,
    allow_headers=CORS_HEADERS_PERMITIDOS,
)

# Tradução dos erros de validação automáticos do Pydantic (item M12 do plano).
# Sem isso, o FastAPI responde 422 com mensagens em inglês ("Field required") e com `detail`
# em formato de LISTA — que os clientes web/mobile não sabem exibir. Mapa por `type` do erro;
# tipos não mapeados caem no genérico "tem um valor inválido".
TRADUCAO_ERROS_VALIDACAO = {
    "missing": "é obrigatório",
    "string_too_short": "é muito curto",
    "string_too_long": "é muito longo",
    "string_type": "deve ser um texto",
    "uuid_parsing": "deve ser um identificador (UUID) válido",
    "uuid_type": "deve ser um identificador (UUID) válido",
    "int_parsing": "deve ser um número inteiro",
    "bool_parsing": "deve ser verdadeiro ou falso",
    "enum": "tem um valor fora das opções permitidas",
    "json_invalid": "contém JSON inválido",
    "datetime_parsing": "deve ser uma data/hora válida",
}


# Monta a frase em português de UM erro de validação do Pydantic (ex.: "O campo 'Email' deve
# ser um e-mail válido"). O nome do campo vem de `loc`, ignorando a origem (body/query/...).
def _traduzirErroValidacao(erro: dict) -> str:
    campo = ".".join(
        str(parte) for parte in erro.get("loc", []) if parte not in ("body", "query", "path", "header")
    )
    tipo = erro.get("type", "")
    # EmailStr reporta como `value_error` genérico — detectamos pelo texto original do Pydantic
    if tipo == "value_error" and "email" in erro.get("msg", "").lower():
        descricao = "deve ser um e-mail válido"
    else:
        descricao = TRADUCAO_ERROS_VALIDACAO.get(tipo, "tem um valor inválido")
    return f"O campo '{campo}' {descricao}" if campo else f"A requisição {descricao}"


# Handler global: converte o 422 padrão do FastAPI em `detail` como STRING em português,
# no mesmo formato dos HTTPException das rotas — o front exibe direto, sem tratamento especial.
@app.exception_handler(RequestValidationError)
async def tratarErroValidacao(request: Request, exc: RequestValidationError):
    mensagens = [_traduzirErroValidacao(erro) for erro in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": "; ".join(mensagens)})


# Registra os roteadores de cada módulo com seus prefixos de URL
app.include_router(Autenticacao.roteador)  # /autenticacao/...
app.include_router(Usuarios.roteador)       # /usuarios/...
app.include_router(Chamados.roteador)       # /chamados/...
app.include_router(Plataforma.roteador)     # /plataforma/...
app.include_router(Relatorios.roteador)     # /relatorios/...

# Rota de verificação de saúde da API
@app.get("/")
async def raiz():
    return {"mensagem": "FaciliChat online!"}
