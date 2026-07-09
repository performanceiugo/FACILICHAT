# Configurações da aplicação carregadas do arquivo .env
# Pydantic valida os tipos e lança erro na inicialização se alguma variável estiver ausente

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Configuracoes(BaseSettings):
    # Configuracao Pydantic v2 para carregar variaveis do backend/.env com tolerancia a BOM.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8-sig")

    DATABASE_URL: str            # URL de conexão com o PostgreSQL (ex: postgresql+asyncpg://...)
    JWT_SECRET: str              # Chave secreta para assinar e verificar tokens JWT
    JWT_ALGORITHM: str = "HS256"        # Algoritmo de criptografia do JWT
    # Access token curto (item S15): 15min é o padrão atual (OWASP/2026) para limitar a janela de
    # uso de um token roubado. A sessão continua longa na prática graças ao refresh token, que o
    # cliente troca por um access token novo em segundo plano — ver POST /autenticacao/atualizar.
    JWT_EXPIRE_MINUTES: int = 15
    # Claims `iss`/`aud` (item B6): identificam quem emitiu o token e para quem ele vale. Não são
    # segredo — servem para o `jwt.decode` rejeitar de cara um token emitido por outro serviço ou
    # pensado para outro público, antes mesmo de checar a denylist.
    JWT_ISSUER: str = "facilichat-api"
    JWT_AUDIENCE: str = "facilichat-clientes"
    # Validade do refresh token (item S15) — janela em que o usuário continua "logado" sem digitar
    # a senha de novo, desde que o app chame /autenticacao/atualizar antes de expirar. Cada uso
    # rotaciona o token e renova esta janela (sessão "deslizante"); só expira de vez com inatividade.
    REFRESH_TOKEN_EXPIRE_DIAS: int = 30
    ANTHROPIC_API_KEY: str       # Chave da API da Anthropic para integração com IA
    # Origens (URLs de frontend) autorizadas a chamar a API via navegador, separadas por vírgula.
    # Default cobre o Next.js local; em produção, definir no .env com os domínios reais.
    DEBUG: bool = False
    # Swagger (/docs), ReDoc (/redoc) e o schema (/openapi.json) — item S8. Documentam a API
    # publicamente (rotas, schemas de request/response) e ajudam quem for atacar a mapear a
    # superfície antes de tentar algo. Ligado por padrão (dev depende disso); desligar em produção
    # via `.env` — nenhuma mudança de código entre os dois ambientes.
    API_DOCS_HABILITADO: bool = True
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    # Cadastro publico fica fechado por padrao para impedir que o payload escolha qualquer EmpresaID.
    # Quando habilitado em dev/onboarding assistido, deve apontar para uma unica Empresa ativa.
    CADASTRO_PUBLICO_HABILITADO: bool = False
    CADASTRO_PUBLICO_EMPRESA_ID: str | None = None

    # --- Cookie de sessao do painel web (item S6) ---------------------------------------------
    # Configuraveis por ambiente para que a virada dev -> producao seja um flag, nunca uma edicao
    # de codigo. Defaults sao os SEGUROS (producao); o dev afrouxa no .env quando precisar.
    #
    # COOKIE_SECURE=true faz o navegador so enviar o cookie por HTTPS. Chrome e Firefox aceitam
    # cookies Secure em http://localhost, entao o padrao seguro costuma funcionar em dev tambem.
    COOKIE_SECURE: bool = True
    # SameSite=lax basta porque o painel fala com a API pelo proxy /api/* do Next (mesma origem),
    # o que torna o cookie first-party. "none" so faria sentido em cookie de terceira parte —
    # que e exatamente o cenario que a escolha do proxy evita.
    COOKIE_SAMESITE: str = "lax"
    # Vazio => cookie host-only (so o host exato que o emitiu). Preencher apenas se o cookie
    # precisar valer para subdominios (ex.: ".facilichat.com").
    COOKIE_DOMAIN: str | None = None

    # Valida o SameSite antes de a API subir: um valor invalido faz o navegador descartar o
    # atributo silenciosamente, e a protecao sumiria sem nenhum erro visivel.
    @field_validator("COOKIE_SAMESITE")
    @classmethod
    def validar_cookie_samesite(cls, valor: str) -> str:
        normalizado = valor.strip().lower()
        if normalizado not in {"lax", "strict", "none"}:
            raise ValueError('COOKIE_SAMESITE deve ser "lax", "strict" ou "none"')
        return normalizado

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

    # O navegador DESCARTA um cookie "SameSite=None" que nao seja "Secure" — a combinacao anularia
    # a sessao sem erro nenhum. Falha na subida em vez de deixar o painel quebrado em producao.
    @model_validator(mode="after")
    def validar_coerencia_cookie(self) -> "Configuracoes":
        if self.COOKIE_SAMESITE == "none" and not self.COOKIE_SECURE:
            raise ValueError('COOKIE_SAMESITE="none" exige COOKIE_SECURE=true (regra do navegador)')
        return self

    # Converte a string CSV de CORS_ORIGINS em lista, pronta para o CORSMiddleware do FastAPI
    @property
    def cors_origins_lista(self) -> list[str]:
        return [origem.strip() for origem in self.CORS_ORIGINS.split(",") if origem.strip()]

# Instância global usada em toda a aplicação via importação
configuracoes = Configuracoes()
