# Modelo ORM das coberturas operacionais de posto/turno.
# Registra de forma estruturada quem cobrirá cada período, sem inferir escala de texto livre.

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.banco_dados import Base
from app.tempo import agoraUtc


# Cobertura de um posto em um período; ResponsavelID/ConfirmadaEm nulos significam descoberta.
class CoberturaTurno(Base):
    __tablename__ = "CoberturasTurno"

    ID: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    EmpresaID: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("Empresas.ID"), nullable=False)
    CondominioID: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("Condominios.ID"), nullable=False)
    Posto: Mapped[str] = mapped_column(String(120), nullable=False)
    Turno: Mapped[str] = mapped_column(String(80), nullable=False)
    Inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    Fim: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ResponsavelID: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("Usuarios.ID"), nullable=True)
    ConfirmadaEm: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    Criacao: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agoraUtc, nullable=False)
