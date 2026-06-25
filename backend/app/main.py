from fastapi import FastAPI
from BancoDados import engine, Base
import Modelos
from Rotas import Autenticacao, Usuarios, Chamados

app = FastAPI(
    title="FaciliChat",
    description="Plataforma de atendimento para gestão de condomínios",
    version="0.1.0"
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Banco de dados conectado!")

app.include_router(Autenticacao.roteador)
app.include_router(Usuarios.roteador)
app.include_router(Chamados.roteador)

@app.get("/")
async def raiz():
    return {"mensagem": "FaciliChat online!"}
