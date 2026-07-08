# Modelo ORM da tabela Usuarios
# Representa todos os perfis de usuário do sistema: moradores, funcionários, supervisores, back-office e gestores

from sqlalchemy import String, Enum as SAEnum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
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

    ID: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Tenant do usuário (regra de ouro da Fase 0.7: toda tabela pertence a uma Empresa).
    # Nota: hoje todo Usuario — inclusive Superadmin — precisa de uma Empresa; um Superadmin
    # "sem empresa" fica fora do escopo desta entrega (não há UI/rota que crie esse caso).
    EmpresaID: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("Empresas.ID"), nullable=False)
    Nome: Mapped[str] = mapped_column(String(120), nullable=False)
    Email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    SenhaHash: Mapped[str] = mapped_column(String(255), nullable=False)  # Senha armazenada como hash argon2 (nunca texto puro)
    Funcao: Mapped[UsuarioFuncao] = mapped_column(SAEnum(UsuarioFuncao), nullable=False)
    Telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    Condominio: Mapped[str | None] = mapped_column(String(120), nullable=True)  # Condomínio ao qual o usuário pertence
    Criacao: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow)
