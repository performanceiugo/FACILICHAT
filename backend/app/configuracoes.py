# Configurações da aplicação carregadas do arquivo .env
# Pydantic valida os tipos e lança erro na inicialização se alguma variável estiver ausente

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Configuracoes(BaseSettings):
    # Configuracao Pydantic v2 para carregar variaveis do backend/.env com tolerancia a BOM.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8-sig")

    DATABASE_URL: str            # URL de conexão com o PostgreSQL (ex: postgresql+asyncpg://...)
    JWT_SECRET: str              # Chave secreta para assinar e verificar tokens JWT
    JWT_ALGORITHM: str = "HS256"        # Algoritmo de criptografia do JWT
    JWT_EXPIRE_MINUTES: int = 480       # Tempo de expiração do token (padrão: 8 horas)
    ANTHROPIC_API_KEY: str       # Chave da API da Anthropic para integração com IA
    # Origens (URLs de frontend) autorizadas a chamar a API via navegador, separadas por vírgula.
    # Default cobre o Next.js local; em produção, definir no .env com os domínios reais.
    DEBUG: bool = False
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    # Cadastro publico fica fechado por padrao para impedir que o payload escolha qualquer EmpresaID.
    # Quando habilitado em dev/onboarding assistido, deve apontar para uma unica Empresa ativa.
    CADASTRO_PUBLICO_HABILITADO: bool = False
    CADASTRO_PUBLICO_EMPRESA_ID: str | None = None

    # Valida o segredo usado pelo HS256 antes de a API iniciar; segredo curto ou placeholder
    # enfraquece a assinatura dos tokens e deve falhar cedo em qualquer ambiente.
    @field_validator("JWT_SECRET")
    @classmethod
    def validar_jwt_secret(cls, valor: str) -> str:
        placeholders = {
            "sua_chave_secreta_aqui",
            "sua-chave-secreta-aqui",
            "coloque-aqui-uma-chave-aleatoria-longa",
            "dev_secret_change_me",
            "facilichat-dev-secret-key-troque-em-producao",
        }
        if valor in placeholders or len(valor.encode("utf-8")) < 32:
            raise ValueError("JWT_SECRET deve ser aleatório, secreto e ter pelo menos 32 bytes")
        return valor

    # Converte a string CSV de CORS_ORIGINS em lista, pronta para o CORSMiddleware do FastAPI
    @property
    def cors_origins_lista(self) -> list[str]:
        return [origem.strip() for origem in self.CORS_ORIGINS.split(",") if origem.strip()]

# Instância global usada em toda a aplicação via importação
configuracoes = Configuracoes()
