# Modelo ORM da tabela Usuarios
# Representa todos os perfis de usuário do sistema: moradores, funcionários, supervisores, back-office e gestores

from sqlalchemy import Column, String, Enum as SAEnum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.banco_dados import Base
import uuid
import enum
from datetime import datetime

# Enum com os 7 perfis de acesso definidos pelo branding (docs/FaciliChat-Regras/).
# Funcionário é perfil único (sem subtipos limpeza/portaria/zelador) — decisão de produto.
class UsuarioFuncao(str, enum.Enum):
    Cliente = "Cliente"          # Síndico/responsável do Condomínio — abre e acompanha chamados
    Supervisor = "Supervisor"    # Coordenador — visualiza todos os chamados e gerencia prioridades
    Funcionario = "Funcionario"  # Equipe operacional — executa chamados atribuídos
    RH = "RH"                    # Back-office — fila de questões de pessoal
    Financeiro = "Financeiro"    # Back-office — fila de cobranças e pagamentos
    Gestor = "Gestor"            # Dono/gestor da Empresa — acesso completo e relatórios (era "Gerente")
    Superadmin = "Superadmin"    # Iugo Performance — opera a plataforma, cadastra Empresas (Fase 0.7)

# Tabela Usuarios no banco de dados
class Usuario(Base):
    __tablename__ = "Usuarios"

    ID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Tenant do usuário (regra de ouro da Fase 0.7: toda tabela pertence a uma Empresa).
    # Nota: hoje todo Usuario — inclusive Superadmin — precisa de uma Empresa; um Superadmin
    # "sem empresa" fica fora do escopo desta entrega (não há UI/rota que crie esse caso).
    EmpresaID = Column(UUID(as_uuid=True), ForeignKey("Empresas.ID"), nullable=False)
    Nome = Column(String(120), nullable=False)
    Email = Column(String(120), unique=True, nullable=False)
    SenhaHash = Column(String(255), nullable=False)  # Senha armazenada como hash argon2 (nunca texto puro)
    Funcao = Column(SAEnum(UsuarioFuncao), nullable=False)
    Telefone = Column(String(20), nullable=True)
    Condominio = Column(String(120), nullable=True)  # Condomínio ao qual o usuário pertence
    Criacao = Column(DateTime, default=datetime.utcnow)
