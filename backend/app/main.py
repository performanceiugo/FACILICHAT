# Ponto de entrada da aplicação FaciliChat
# Inicializa o FastAPI, cria as tabelas no banco de dados e registra as rotas

from fastapi import FastAPI
from BancoDados import engine, Base
import Modelos  # importação necessária para que o SQLAlchemy reconheça os modelos antes do create_all
from Rotas import Autenticacao, Usuarios, Chamados

# Instância principal da aplicação — título e versão aparecem no Swagger (/docs)
app = FastAPI(
    title="FaciliChat",
    description="Plataforma de atendimento para gestão de condomínios",
    version="0.1.0"
)

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

# Rota de verificação de saúde da API
@app.get("/")
async def raiz():
    return {"mensagem": "FaciliChat online!"}
