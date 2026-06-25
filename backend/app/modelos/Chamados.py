from sqlalchemy import Column, String, Enum as SAEnum, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from BancoDados import Base
import uuid
import enum
from datetime import datetime

class ChamadoFila(str, enum.Enum):
    Operacional = "Operacional"
    RH = "RH"
    Financeiro = "Financeiro"

class ChamadoStatus(str, enum.Enum):
    Recebido = "Recebido"
    EmAndamento = "EmAndamento"
    Agendado = "Agendado"
    Concluido = "Concluido"
    Cancelado = "Cancelado"

class ChamadoPrioridade(str, enum.Enum):
    Baixa = "Baixa"
    Media = "Media"
    Alta = "Alta"
    Critica = "Critica"

class Chamado(Base):
    __tablename__ = "Chamados"

    ID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ClienteID = Column(UUID(as_uuid=True), ForeignKey("Usuarios.ID"), nullable=False)
    SupervisorID = Column(UUID(as_uuid=True), ForeignKey("Usuarios.ID"), nullable=True)
    Fila = Column(SAEnum(ChamadoFila), nullable=False)
    Categoria = Column(String(80), nullable=False)
    Status = Column(SAEnum(ChamadoStatus), default=ChamadoStatus.Recebido)
    Prioridade = Column(SAEnum(ChamadoPrioridade), default=ChamadoPrioridade.Media)
    Resumo = Column(Text, nullable=True)
    PrazoSLA = Column(DateTime, nullable=True)
    Criacao = Column(DateTime, default=datetime.utcnow)
    Atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    Cliente = relationship("Usuario", foreign_keys=[ClienteID])
    Supervisor = relationship("Usuario", foreign_keys=[SupervisorID])
    Mensagens = relationship("Mensagem", back_populates="Chamado")
