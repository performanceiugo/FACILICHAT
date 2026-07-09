# Modelo ORM da tabela Mensagens
# Armazena o histórico do chat interno de cada chamado
# Mensagens podem ser enviadas por humanos ou geradas pela IA do sistema

from sqlalchemy import String, Enum as SAEnum, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.banco_dados import Base
from app.tempo import agoraUtc
import uuid
import enum
from datetime import datetime

# Tipo de autor da mensagem — diferencia humanos de IA e notificações automáticas do sistema
class AutorTipo(str, enum.Enum):
    Cliente = "Cliente"
    Supervisor = "Supervisor"
    Funcionario = "Funcionario"
    IA = "IA"           # Mensagem gerada pela inteligência artificial (Anthropic)
    Sistema = "Sistema"  # Notificação automática (ex: "Status alterado para Em Andamento")

# Tabela Mensagens no banco de dados
class Mensagem(Base):
    __tablename__ = "Mensagens"

    ID: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    EmpresaID: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("Empresas.ID"), nullable=False)  # Tenant (Fase 0.7)
    ChamadoID: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("Chamados.ID"), nullable=False)
    AutorID: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("Usuarios.ID"), nullable=True)  # Nulo quando AutorTipo é IA ou Sistema
    AutorTipo: Mapped[AutorTipo] = mapped_column(SAEnum(AutorTipo), nullable=False)
    Conteudo: Mapped[str] = mapped_column(Text, nullable=False)
    Anexo: Mapped[str | None] = mapped_column(String(500), nullable=True)  # URL de arquivo ou imagem anexada
    Criacao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=agoraUtc)

    # Relacionamentos ORM
    Chamado = relationship("Chamado", back_populates="Mensagens")
    Autor = relationship("Usuario", foreign_keys=[AutorID])
