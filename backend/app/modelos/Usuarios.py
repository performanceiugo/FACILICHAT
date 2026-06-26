# Modelo ORM da tabela Usuarios
# Representa todos os perfis de usuário do sistema: moradores, funcionários, supervisores e gerentes

from sqlalchemy import Column, String, Enum as SAEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from BancoDados import Base
import uuid
import enum
from datetime import datetime

# Enum com os perfis de acesso disponíveis no sistema
class UsuarioFuncao(str, enum.Enum):
    Cliente = "Cliente"          # Morador — abre e acompanha chamados
    Supervisor = "Supervisor"    # Coordenador — visualiza todos os chamados e gerencia prioridades
    Funcionario = "Funcionario"  # Equipe operacional — executa chamados atribuídos
    Gerente = "Gerente"          # Gestão geral — acesso completo e relatórios

# Tabela Usuarios no banco de dados
class Usuario(Base):
    __tablename__ = "Usuarios"

    ID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    Nome = Column(String(120), nullable=False)
    Email = Column(String(120), unique=True, nullable=False)
    SenhaHash = Column(String(255), nullable=False)  # Senha armazenada como hash argon2 (nunca texto puro)
    Funcao = Column(SAEnum(UsuarioFuncao), nullable=False)
    Telefone = Column(String(20), nullable=True)
    Condominio = Column(String(120), nullable=True)  # Condomínio ao qual o usuário pertence
    Criacao = Column(DateTime, default=datetime.utcnow)
