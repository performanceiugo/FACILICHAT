# Modelo ORM da tabela Chamados (solicitações de serviço)
# Um chamado é criado pelo Cliente e percorre um fluxo de status até ser concluído ou cancelado

from sqlalchemy import String, Enum as SAEnum, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.banco_dados import Base
import uuid
import enum
from datetime import datetime

# Filas de atendimento — cada chamado é direcionado a uma das quatro equipes.
# Nota: esta fila (roteamento do chamado) é um enum separado do UsuarioFuncao (perfil do usuário);
# os nomes RH/Financeiro coincidem propositalmente, mas não são a mesma coisa.
class ChamadoFila(str, enum.Enum):
    Operacional = "Operacional"  # Manutenção, limpeza, portaria, etc.
    RH = "RH"                   # Questões de pessoal e recursos humanos
    Financeiro = "Financeiro"    # Cobranças, pagamentos e taxas condominiais
    Comercial = "Comercial"      # Oportunidade de venda/serviço extra — roteada ao Gestor

# Ciclo de vida de um chamado: Recebido → Em Andamento → Agendado → Concluído / Cancelado
class ChamadoStatus(str, enum.Enum):
    Recebido = "Recebido"
    EmAndamento = "EmAndamento"
    Agendado = "Agendado"
    Concluido = "Concluido"
    Cancelado = "Cancelado"

# Nível de urgência definido pelo cliente no momento da abertura
class ChamadoPrioridade(str, enum.Enum):
    Baixa = "Baixa"
    Media = "Media"
    Alta = "Alta"
    Critica = "Critica"  # Exige atenção imediata

# Tabela Chamados no banco de dados
class Chamado(Base):
    __tablename__ = "Chamados"

    ID: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    EmpresaID: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("Empresas.ID"), nullable=False)  # Tenant (Fase 0.7)
    ClienteID: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("Usuarios.ID"), nullable=False)   # Quem abriu o chamado
    GrupoOrigemID: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)       # Tickets irmãos do mesmo aviso
    SupervisorID: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("Usuarios.ID"), nullable=True) # Responsável atribuído (opcional)
    Fila: Mapped[ChamadoFila] = mapped_column(SAEnum(ChamadoFila), nullable=False)
    Categoria: Mapped[str] = mapped_column(String(80), nullable=False)           # Ex: "Elétrica", "Hidráulica", "Segurança"
    Status: Mapped[ChamadoStatus | None] = mapped_column(SAEnum(ChamadoStatus), default=ChamadoStatus.Recebido)
    Prioridade: Mapped[ChamadoPrioridade | None] = mapped_column(SAEnum(ChamadoPrioridade), default=ChamadoPrioridade.Media)
    Resumo: Mapped[str | None] = mapped_column(Text, nullable=True)                     # Descrição livre do problema
    PrazoSLA: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)          # Prazo de atendimento conforme acordo de nível de serviço
    Criacao: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow)
    Atualizacao: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos ORM — permitem acessar chamado.Cliente, chamado.Mensagens, etc.
    Cliente = relationship("Usuario", foreign_keys=[ClienteID])
    Supervisor = relationship("Usuario", foreign_keys=[SupervisorID])
    Mensagens = relationship("Mensagem", back_populates="Chamado")
