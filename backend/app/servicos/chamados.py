import uuid
from typing import Protocol, Sequence

from app.modelos.Chamados import Chamado, ChamadoFila, ChamadoPrioridade
from app.modelos.Usuarios import Usuario


class ChamadoPayload(Protocol):
    Fila: ChamadoFila
    Categoria: str
    Resumo: str | None
    Prioridade: ChamadoPrioridade


def montarChamadosIrmaos(payloads: Sequence[ChamadoPayload], usuarioAtual: Usuario) -> list[Chamado]:
    grupoOrigemID = uuid.uuid4()
    return [
        Chamado(
            EmpresaID=usuarioAtual.EmpresaID,
            ClienteID=usuarioAtual.ID,
            GrupoOrigemID=grupoOrigemID,
            Fila=payload.Fila,
            Categoria=payload.Categoria,
            Resumo=payload.Resumo,
            Prioridade=payload.Prioridade,
        )
        for payload in payloads
    ]
