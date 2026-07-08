# Configuração da conexão assíncrona com o PostgreSQL
# Usa SQLAlchemy 2.0 com asyncpg como driver de baixo nível

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.configuracoes import configuracoes

# Engine assíncrono — echo=True imprime todas as queries SQL no console (útil em desenvolvimento)
engine = create_async_engine(configuracoes.DATABASE_URL, echo=True)

# Fábrica de sessões dedicada ao asyncio (SQLAlchemy 2.0) — expire_on_commit=False evita erros
# ao acessar atributos após o commit
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Classe base para todos os modelos ORM do projeto
class Base(DeclarativeBase):
    pass

# Dependência injetável no FastAPI — abre e fecha a sessão automaticamente por requisição
async def obterBancoDados():
    async with AsyncSessionLocal() as session:
        yield session
