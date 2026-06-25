from pydantic_settings import BaseSettings

class Configuracoes(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480
    ANTHROPIC_API_KEY: str

    class Config:
        env_file = ".env"

configuracoes = Configuracoes()
