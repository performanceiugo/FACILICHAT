# Configurações da aplicação carregadas do arquivo .env
# Pydantic valida os tipos e lança erro na inicialização se alguma variável estiver ausente

from pydantic_settings import BaseSettings

class Configuracoes(BaseSettings):
    DATABASE_URL: str            # URL de conexão com o PostgreSQL (ex: postgresql+asyncpg://...)
    JWT_SECRET: str              # Chave secreta para assinar e verificar tokens JWT
    JWT_ALGORITHM: str = "HS256"        # Algoritmo de criptografia do JWT
    JWT_EXPIRE_MINUTES: int = 480       # Tempo de expiração do token (padrão: 8 horas)
    ANTHROPIC_API_KEY: str       # Chave da API da Anthropic para integração com IA
    # Origens (URLs de frontend) autorizadas a chamar a API via navegador, separadas por vírgula.
    # Default cobre o Next.js local; em produção, definir no .env com os domínios reais.
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    class Config:
        env_file = ".env"  # Lê variáveis do arquivo .env na raiz do backend

    # Converte a string CSV de CORS_ORIGINS em lista, pronta para o CORSMiddleware do FastAPI
    @property
    def cors_origins_lista(self) -> list[str]:
        return [origem.strip() for origem in self.CORS_ORIGINS.split(",") if origem.strip()]

# Instância global usada em toda a aplicação via importação
configuracoes = Configuracoes()
