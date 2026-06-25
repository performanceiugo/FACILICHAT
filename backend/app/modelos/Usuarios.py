from sqlalchemy import Column, String, Enum as SAEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from BancoDados import Base
import uuid
import enum
from datetime import datetime

class UsuarioFuncao(str, enum.Enum):
    Cliente = "Cliente"
    Supervisor = "Supervisor"
    Funcionario = "Funcionario"
    Gerente = "Gerente"

class Usuario(Base):
    __tablename__ = "Usuarios"

    ID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    Nome = Column(String(120), nullable=False)
    Email = Column(String(120), unique=True, nullable=False)
    SenhaHash = Column(String(255), nullable=False)
    Funcao = Column(SAEnum(UsuarioFuncao), nullable=False)
    Telefone = Column(String(20), nullable=True)
    Condominio = Column(String(120), nullable=True)
    Criacao = Column(DateTime, default=datetime.utcnow)
