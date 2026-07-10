# Utilitarios leves de seguranca para fluxos publicos de autenticacao.
# Mantem rate limit em memoria para reduzir abuso em dev/single-process sem adicionar dependencia externa.

from dataclasses import dataclass
from time import monotonic

from fastapi import HTTPException, Request


# Estado de uma chave de rate limit dentro da janela atual.
@dataclass
class JanelaRateLimit:
    # Instante monotônico em que a janela começou; não depende do relógio civil do servidor.
    inicio: float
    # Quantidade de requisições já contabilizadas na janela corrente.
    tentativas: int = 0
    # Instante monotônico até o qual a chave permanece bloqueada; zero significa sem bloqueio.
    bloqueadoAte: float = 0.0


# Registro em memoria por processo. Em producao com multiplas replicas, substituir por Redis ou similar.
_janelasRateLimit: dict[str, JanelaRateLimit] = {}


# Normaliza identificadores publicos antes de compor chaves de rate limit.
def normalizarIdentificador(valor: str | None) -> str:
    return (valor or "").strip().lower() or "desconhecido"


# Extrai o IP de origem considerando proxy reverso simples; se o header nao existir, usa o client.host.
def obterIpCliente(request: Request) -> str:
    encaminhado = request.headers.get("x-forwarded-for")
    if encaminhado:
        return encaminhado.split(",")[0].strip()
    return request.client.host if request.client else "desconhecido"


# Aplica limite por IP e por identificador logico (email) para login/signup.
def aplicarRateLimitAutenticacao(
    escopo: str,
    request: Request,
    identificador: str,
    limite: int = 5,
    janelaSegundos: int = 300,
    bloqueioSegundos: int = 900,
) -> None:
    # `monotonic` evita que ajustes no relógio do sistema encurtem ou prolonguem a proteção.
    agora = monotonic()

    # A mesma tentativa consome os limites do endereço de origem e do identificador informado.
    # Isso reduz tanto ataques distribuídos contra uma conta quanto várias contas a partir de um IP.
    chaves = [
        f"{escopo}:ip:{obterIpCliente(request)}",
        f"{escopo}:id:{normalizarIdentificador(identificador)}",
    ]

    # Avalia cada dimensão separadamente; qualquer uma bloqueada interrompe a requisição.
    for chave in chaves:
        janela = _janelasRateLimit.get(chave)

        # Chaves novas ou com janela expirada recomeçam a contagem do zero.
        if not janela or agora - janela.inicio > janelaSegundos:
            janela = JanelaRateLimit(inicio=agora)
            _janelasRateLimit[chave] = janela

        # Um bloqueio já aplicado continua valendo até o instante registrado.
        if janela.bloqueadoAte > agora:
            raise HTTPException(
                status_code=429,
                detail="Muitas tentativas. Aguarde alguns minutos e tente novamente.",
            )

        # A tentativa atual é registrada antes da comparação para bloquear somente ao exceder o limite.
        janela.tentativas += 1
        if janela.tentativas > limite:
            # Ao exceder o limite, preserva a janela e define quando novas tentativas serão aceitas.
            janela.bloqueadoAte = agora + bloqueioSegundos
            raise HTTPException(
                status_code=429,
                detail="Muitas tentativas. Aguarde alguns minutos e tente novamente.",
            )
