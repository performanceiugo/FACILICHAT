# Modelo ORM da tabela SessaoRevogada — denylist de tokens JWT revogados (item S14 do plano).
#
# Por que existe: o JWT é stateless por natureza, então um logout sozinho não invalida o token no
# servidor — quem já copiou o token continua autenticado até ele expirar. Esta tabela guarda o
# `jti` (ID único de cada token, ver claim em Autenticacao.criarToken) de todo token explicitamente
# revogado no logout; `obterUsuarioAtual`/`obterTenantAtual` consultam por ele a cada requisição.
#
# `ExpiraEm` é a mesma expiração (`exp`) do JWT original: depois desse instante o token já seria
# rejeitado por expiração mesmo sem estar na denylist, então a entrada pode ser apagada com
# segurança. Sem Redis no stack atual, a limpeza é feita "na unha" (DELETE por ExpiraEm vencido)
# a cada novo logout, em vez de TTL automático — ver `registrarRevogacao` em servicos/revogacao.py.
#
# `EmpresaID` não é usado em nenhuma query (o `jti` já é globalmente único e opaco, sem dado de
# negócio), mas é mantido por consistência com a regra de ouro da Fase 0.7 ("toda tabela pertence
# a uma Empresa") e para facilitar auditoria futura. Deliberadamente FORA da RLS (rls.sql): a
# checagem de denylist roda em `obterBancoDados` puro, antes/sem `app.empresa_id` setado — se esta
# tabela tivesse FORCE ROW LEVEL SECURITY, a query de revogação sempre veria zero linhas (fail-
# closed) e o próprio mecanismo de revogação nunca funcionaria.

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.banco_dados import Base
import uuid
from datetime import datetime


class SessaoRevogada(Base):
    __tablename__ = "SessoesRevogadas"

    # O próprio jti é a chave primária: cada token revogado gera no máximo uma entrada.
    Jti: Mapped[str] = mapped_column(String(64), primary_key=True)
    EmpresaID: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("Empresas.ID"), nullable=False)
    UsuarioID: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("Usuarios.ID"), nullable=False)
    ExpiraEm: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
