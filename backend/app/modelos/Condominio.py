# Modelo ORM da tabela Condominios
# Representa o cliente atendido pela Empresa (tenant) e substitui gradualmente o antigo campo
# textual Usuario.Condominio por uma entidade propria, sem antecipar ainda o CRUD completo da Fase 7.

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.banco_dados import Base
import uuid
from datetime import datetime


# Tabela Condominios no banco de dados
class Condominio(Base):
    __tablename__ = "Condominios"

    ID: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    EmpresaID: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("Empresas.ID"), nullable=False)
    Nome: Mapped[str] = mapped_column(String(150), nullable=False)
    Criacao: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow)
