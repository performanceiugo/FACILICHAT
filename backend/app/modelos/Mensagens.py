from sqlalchemy import Column, String, Enum as SAEnum, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from BancoDados import Base
import uuid
import enum
from datetime import datetime

class AutorTipo(str, enum.Enum):
    Cliente = "Cliente"
    Supervisor = "Supervisor"
    Funcionario = "Funcionario"
    IA = "IA"
    Sistema = "Sistema"

class Mensagem(Base):
    __tablename__ = "Mensagens"

    ID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ChamadoID = Column(UUID(as_uuid=True), ForeignKey("Chamados.ID"), nullable=False)
    AutorID = Column(UUID(as_uuid=True), ForeignKey("Usuarios.ID"), nullable=True)
    AutorTipo = Column(SAEnum(AutorTipo), nullable=False)
    Conteudo = Column(Text, nullable=False)
    Anexo = Column(String(500), nullable=True)
    Criacao = Column(DateTime, default=datetime.utcnow)

    Chamado = relationship("Chamado", back_populates="Mensagens")
    Autor = relationship("Usuario", foreign_keys=[AutorID])
