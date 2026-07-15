# Modelo ORM da tabela Empresas
# A Empresa é o tenant do SaaS: uma conservadora/empresa de facilities (ex.: "Cefram") que contrata
# o FaciliChat para atender os Condomínios dela. Todo dado do sistema pertence a uma Empresa
# (ver docs/plano-implementacao.md — Fase 0.7, Fundação SaaS Multi-Tenant).

from sqlalchemy import Boolean, String, Enum as SAEnum, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.banco_dados import Base
from app.tempo import agoraUtc
import uuid
import enum
from datetime import datetime

# Situação comercial da Empresa perante a plataforma — controlada pelo Superadmin (Iugo Performance)
class EmpresaStatus(str, enum.Enum):
    Ativa = "Ativa"
    Suspensa = "Suspensa"

# Tabela Empresas no banco de dados
class Empresa(Base):
    __tablename__ = "Empresas"

    ID: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    Nome: Mapped[str] = mapped_column(String(150), nullable=False)
    CNPJ: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    Status: Mapped[EmpresaStatus] = mapped_column(SAEnum(EmpresaStatus), default=EmpresaStatus.Ativa, nullable=False)
    # Marca a Empresa que hospeda o(s) Superadmin(s) da Iugo Performance (criada por
    # `scripts/gerenciar_banco.py criar-superadmin`) — existe só porque `Usuario.EmpresaID` é
    # NOT NULL (regra de ouro da Fase 0.7), não porque a Iugo é um tenant de verdade. `False` para
    # toda Empresa-cliente normal. `GET /plataforma/empresas` filtra por este campo para a tela do
    # Superadmin listar só os tenants reais, e `PATCH .../status` recusa alterar o status desta
    # Empresa (suspendê-la trancaria todos os Superadmins para fora da própria plataforma).
    EhPlataforma: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    Criacao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=agoraUtc)


# Configurações operacionais por tenant ficam em tabela separada para que instalações existentes
# recebam o novo schema via create_all, sem ALTER destrutivo enquanto Alembic ainda está pendente.
class EmpresaConfiguracao(Base):
    __tablename__ = "EmpresaConfiguracoes"

    EmpresaID: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("Empresas.ID"),
        primary_key=True,
    )
    # 72h é apenas o valor inicial; cada Gestor pode substituí-lo pela API da própria Empresa.
    LimiteGargaloHoras: Mapped[int] = mapped_column(Integer, default=72, nullable=False)
