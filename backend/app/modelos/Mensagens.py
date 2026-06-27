# Modelo ORM da tabela Mensagens
# Armazena o histórico do chat interno de cada chamado
# Mensagens podem ser enviadas por humanos ou geradas pela IA do sistema

from sqlalchemy import Column, String, Enum as SAEnum, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.banco_dados import Base
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

    ID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ChamadoID = Column(UUID(as_uuid=True), ForeignKey("Chamados.ID"), nullable=False)
    AutorID = Column(UUID(as_uuid=True), ForeignKey("Usuarios.ID"), nullable=True)  # Nulo quando AutorTipo é IA ou Sistema
    AutorTipo = Column(SAEnum(AutorTipo), nullable=False)
    Conteudo = Column(Text, nullable=False)
    Anexo = Column(String(500), nullable=True)  # URL de arquivo ou imagem anexada
    Criacao = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos ORM
    Chamado = relationship("Chamado", back_populates="Mensagens")
    Autor = relationship("Usuario", foreign_keys=[AutorID])
