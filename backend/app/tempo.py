# Utilitarios de tempo compartilhados pela API.
# Mantem timestamps sempre timezone-aware em UTC, evitando datetime naive/deprecado.

from datetime import datetime, timezone


# Retorna o instante atual em UTC com tzinfo, pronto para colunas DateTime(timezone=True).
def agoraUtc() -> datetime:
    return datetime.now(timezone.utc)

