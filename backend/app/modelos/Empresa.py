# Modelo ORM da tabela Empresas
# A Empresa é o tenant do SaaS: uma conservadora/empresa de facilities (ex.: "Cefram") que contrata
# o FaciliChat para atender os Condomínios dela. Todo dado do sistema pertence a uma Empresa
# (ver docs/plano-implementacao.md — Fase 0.7, Fundação SaaS Multi-Tenant).

from sqlalchemy import Column, String, Enum as SAEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.banco_dados import Base
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

    ID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    Nome = Column(String(150), nullable=False)
    CNPJ = Column(String(20), unique=True, nullable=False)
    Status = Column(SAEnum(EmpresaStatus), default=EmpresaStatus.Ativa, nullable=False)
    Criacao = Column(DateTime, default=datetime.utcnow)
