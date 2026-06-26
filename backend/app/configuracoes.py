# Configurações da aplicação carregadas do arquivo .env
# Pydantic valida os tipos e lança erro na inicialização se alguma variável estiver ausente

from pydantic_settings import BaseSettings

class Configuracoes(BaseSettings):
    DATABASE_URL: str            # URL de conexão com o PostgreSQL (ex: postgresql+asyncpg://...)
    JWT_SECRET: str              # Chave secreta para assinar e verificar tokens JWT
    JWT_ALGORITHM: str = "HS256"        # Algoritmo de criptografia do JWT
    JWT_EXPIRE_MINUTES: int = 480       # Tempo de expiração do token (padrão: 8 horas)
    ANTHROPIC_API_KEY: str       # Chave da API da Anthropic para integração com IA

    class Config:
        env_file = ".env"  # Lê variáveis do arquivo .env na raiz do backend

# Instância global usada em toda a aplicação via importação
configuracoes = Configuracoes()
