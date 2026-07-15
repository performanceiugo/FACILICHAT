# Modelo ORM do catálogo de categorias de chamado.
# Cada Empresa mantém seu próprio catálogo (regra de modelagem da Fase 4: nada de nome fixo em
# enum/constante) — os chamados passam a referenciar uma linha daqui em vez de texto livre.

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.banco_dados import Base
from app.tempo import agoraUtc


# Categoria de chamado pertencente a uma Empresa. `Ativa=False` é a forma de "remover" uma
# categoria sem quebrar os chamados que já a referenciam (tese anti-amnésia: nunca exclusão).
class CategoriaChamado(Base):
    __tablename__ = "CategoriasChamado"

    ID: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    EmpresaID: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("Empresas.ID"), nullable=False)
    Nome: Mapped[str] = mapped_column(String(80), nullable=False)
    Ativa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    Criacao: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agoraUtc, nullable=False)
