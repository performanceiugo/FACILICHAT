# Ponto de entrada da aplicação FaciliChat
# Inicializa o FastAPI, cria as tabelas no banco de dados e registra as rotas

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.banco_dados import engine, Base
from app.configuracoes import configuracoes
from app import modelos  # importação necessária para que o SQLAlchemy reconheça os modelos antes do create_all
from app.rotas import Autenticacao, Usuarios, Chamados, Plataforma

# Instância principal da aplicação — título e versão aparecem no Swagger (/docs)
app = FastAPI(
    title="FaciliChat",
    description="Plataforma de atendimento para gestão de condomínios",
    version="0.1.0"
)

# CORS — libera os frontends (web/mobile) configurados a chamar a API pelo navegador.
# Origens explícitas (nunca "*" junto de allow_credentials) vindas das configurações/.env.
app.add_middleware(
    CORSMiddleware,
    allow_origins=configuracoes.cors_origins_lista,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


# Cria todas as tabelas no banco ao iniciar o servidor (somente se ainda não existirem)
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Banco de dados conectado!")

# Registra os roteadores de cada módulo com seus prefixos de URL
app.include_router(Autenticacao.roteador)  # /autenticacao/...
app.include_router(Usuarios.roteador)       # /usuarios/...
app.include_router(Chamados.roteador)       # /chamados/...
app.include_router(Plataforma.roteador)     # /plataforma/...

# Rota de verificação de saúde da API
@app.get("/")
async def raiz():
    return {"mensagem": "FaciliChat online!"}
