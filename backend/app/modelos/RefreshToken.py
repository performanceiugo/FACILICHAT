# Modelo ORM da tabela RefreshTokens (item S15 do plano).
#
# Guarda os refresh tokens em uso, no formato opaco "{ID}.{segredo}" — o cliente recebe o valor
# completo, mas só o `ID` (chave primária, usado para o lookup indexado) e o HASH sha256 do
# segredo ficam no banco. Igual senha: mesmo com um vazamento do banco, ninguém recupera o valor
# original para se passar pelo usuário — ver `app/servicos/refresh.py`.
#
# `FamiliaID` é o que permite a rotação com detecção de reuso (recomendação atual da OWASP/2026):
# todo refresh token nascido do mesmo login compartilha a mesma família. A cada troca, o token
# usado é marcado revogado e um novo nasce na mesma família. Se um token JÁ revogado for
# apresentado de novo — sinal de furto/replay —, a família inteira é revogada de uma vez.

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.banco_dados import Base
import uuid
from datetime import datetime


class RefreshToken(Base):
    __tablename__ = "RefreshTokens"

    ID: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    SegredoHash: Mapped[str] = mapped_column(String(64), nullable=False)
    FamiliaID: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    UsuarioID: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("Usuarios.ID"), nullable=False)
    # Ver nota de EmpresaID/RLS em SessaoRevogada.py — mesma lógica se aplica aqui: mantido por
    # consistência com a regra de ouro da Fase 0.7, mas fora da RLS de propósito (fail-closed
    # quebraria o próprio mecanismo de autenticação).
    EmpresaID: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("Empresas.ID"), nullable=False)
    CriadoEm: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ExpiraEm: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # Preenchido quando o token é consumido (rotação normal) OU quando a família inteira é
    # revogada (logout ou reuso detectado). NULL = ainda válido para uma próxima rotação.
    RevogadoEm: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
