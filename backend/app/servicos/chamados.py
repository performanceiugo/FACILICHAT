# Serviço de domínio para construção de chamados relacionados.
# Centraliza a criação de tickets irmãos para que todos compartilhem a mesma origem e tenant.

import uuid
from typing import Protocol, Sequence

from app.modelos.Chamados import Chamado, ChamadoFila, ChamadoPrioridade
from app.modelos.Usuarios import Usuario


# Contrato mínimo aceito pelo serviço ao montar cada chamado irmão.
# O Protocol evita acoplar esta regra a um schema Pydantic específico da camada de rotas.
class ChamadoPayload(Protocol):
    Fila: ChamadoFila
    CategoriaID: uuid.UUID
    Resumo: str | None
    Prioridade: ChamadoPrioridade


# Constrói dois ou mais chamados nascidos do mesmo aviso, sem gravá-los no banco.
# A rota chamadora continua responsável por validar cada CategoriaID (ativa/mesma Empresa) antes de
# chamar esta função, e também pela persistência e resposta HTTP.
def montarChamadosIrmaos(payloads: Sequence[ChamadoPayload], usuarioAtual: Usuario) -> list[Chamado]:
    # Um único identificador liga todos os tickets criados nesta operação para preservar a rastreabilidade.
    grupoOrigemID = uuid.uuid4()

    # Cada chamado herda o tenant e o cliente autenticado; somente os dados operacionais vêm do payload.
    return [
        Chamado(
            EmpresaID=usuarioAtual.EmpresaID,
            ClienteID=usuarioAtual.ID,
            GrupoOrigemID=grupoOrigemID,
            Fila=payload.Fila,
            CategoriaID=payload.CategoriaID,
            Resumo=payload.Resumo,
            Prioridade=payload.Prioridade,
        )
        for payload in payloads
    ]
