# Modelo ORM da tabela Chamados (solicitações de serviço)
# Um chamado é criado pelo Cliente e percorre um fluxo de status até ser concluído ou cancelado

from sqlalchemy import Column, String, Enum as SAEnum, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
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

    ID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    EmpresaID = Column(UUID(as_uuid=True), ForeignKey("Empresas.ID"), nullable=False)  # Tenant (Fase 0.7)
    ClienteID = Column(UUID(as_uuid=True), ForeignKey("Usuarios.ID"), nullable=False)   # Quem abriu o chamado
    SupervisorID = Column(UUID(as_uuid=True), ForeignKey("Usuarios.ID"), nullable=True) # Responsável atribuído (opcional)
    Fila = Column(SAEnum(ChamadoFila), nullable=False)
    Categoria = Column(String(80), nullable=False)           # Ex: "Elétrica", "Hidráulica", "Segurança"
    Status = Column(SAEnum(ChamadoStatus), default=ChamadoStatus.Recebido)
    Prioridade = Column(SAEnum(ChamadoPrioridade), default=ChamadoPrioridade.Media)
    Resumo = Column(Text, nullable=True)                     # Descrição livre do problema
    PrazoSLA = Column(DateTime, nullable=True)               # Prazo de atendimento conforme acordo de nível de serviço
    Criacao = Column(DateTime, default=datetime.utcnow)
    Atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos ORM — permitem acessar chamado.Cliente, chamado.Mensagens, etc.
    Cliente = relationship("Usuario", foreign_keys=[ClienteID])
    Supervisor = relationship("Usuario", foreign_keys=[SupervisorID])
    Mensagens = relationship("Mensagem", back_populates="Chamado")
