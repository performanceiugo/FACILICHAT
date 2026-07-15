'use client'

// Página de tickets do Gestor.
// Exibe os chamados do tenant em tabela pesquisável, com filtros operacionais combináveis.

import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { api } from '@/lib/api'
import { auth } from '@/lib/auth'
import { useAtualizacaoPeriodica } from '@/lib/useAtualizacaoPeriodica'
import type { Chamado, ChamadoPrioridade, ChamadoStatus } from '@/types'
import styles from './chamados.module.css'

// Labels simples preservam a linguagem do produto sem expor os valores técnicos dos enums.
const STATUS_LABEL: Record<ChamadoStatus, string> = {
  Recebido: 'Recebido',
  EmAndamento: 'Em andamento',
  Agendado: 'Agendado',
  Concluido: 'Concluído',
  Cancelado: 'Cancelado',
}

// Cada status usa apenas as cores semânticas previstas no design system.
const STATUS_COR: Record<ChamadoStatus, string> = {
  Recebido: 'neutro',
  EmAndamento: 'atencao',
  Agendado: 'info',
  Concluido: 'sucesso',
  Cancelado: 'apagado',
}

// A prioridade recebe um indicador compacto, sem competir visualmente com o status.
const PRIORIDADE_COR: Record<ChamadoPrioridade, string> = {
  Baixa: 'var(--success-500)',
  Media: 'var(--warning-500)',
  Alta: 'var(--danger-500)',
  Critica: 'var(--danger-700)',
}

// Remove diferenças de caixa e acentuação para a busca por cliente ser tolerante à digitação.
function normalizarTexto(valor: string): string {
  return valor.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('pt-BR').trim()
}

// Converte o instante da API em data curta no fuso local do navegador.
function formatarData(valor: string): string {
  return new Date(valor).toLocaleDateString('pt-BR')
}

export default function ChamadosPage() {
  // Dados remotos continuam atualizados pelo polling já adotado no painel.
  const [chamados, setChamados] = useState<Chamado[]>([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState('')
  const [empresaNome, setEmpresaNome] = useState<string | null>(null)
  const montadoRef = useRef(true)

  // Filtros permanecem locais para responder imediatamente e podem ser combinados livremente.
  const [buscaCliente, setBuscaCliente] = useState('')
  const [supervisorID, setSupervisorID] = useState('')
  const [status, setStatus] = useState<ChamadoStatus | ''>('')
  const [categoria, setCategoria] = useState('')
  const [dataInicial, setDataInicial] = useState('')
  const [dataFinal, setDataFinal] = useState('')

  // Busca a última lista sem piscar o carregamento durante atualizações automáticas silenciosas.
  const buscarChamados = useCallback((mostrarCarregando: boolean) => {
    if (mostrarCarregando) setCarregando(true)
    api.chamados.listar()
      .then(lista => {
        if (!montadoRef.current) return
        setChamados(lista)
        if (mostrarCarregando) setErro('')
      })
      .catch((err: unknown) => {
        if (montadoRef.current && mostrarCarregando) {
          setErro(err instanceof Error ? err.message : 'Não foi possível carregar os tickets.')
        }
      })
      .finally(() => {
        if (montadoRef.current && mostrarCarregando) setCarregando(false)
      })
  }, [])

  useEffect(() => {
    montadoRef.current = true
    setEmpresaNome(auth.empresaNome())
    buscarChamados(true)
    return () => { montadoRef.current = false }
  }, [buscarChamados])

  useAtualizacaoPeriodica(() => buscarChamados(false))

  // As opções refletem somente os dados reais disponíveis na Empresa autenticada.
  const categorias = useMemo(
    () => [...new Set(chamados.map(chamado => chamado.Categoria))].sort((a, b) => a.localeCompare(b, 'pt-BR')),
    [chamados],
  )
  const supervisores = useMemo(() => {
    const porID = new Map<string, string>()
    chamados.forEach(chamado => {
      if (chamado.SupervisorID && chamado.SupervisorNome) {
        porID.set(chamado.SupervisorID, chamado.SupervisorNome)
      }
    })
    return [...porID.entries()].sort((a, b) => a[1].localeCompare(b[1], 'pt-BR'))
  }, [chamados])

  // Aplica todos os critérios numa única passagem lógica sem alterar a ordem recebida da API.
  const chamadosFiltrados = useMemo(() => {
    const busca = normalizarTexto(buscaCliente)
    const inicio = dataInicial ? new Date(`${dataInicial}T00:00:00`) : null
    const fim = dataFinal ? new Date(`${dataFinal}T23:59:59.999`) : null

    return chamados.filter(chamado => {
      const criacao = new Date(chamado.Criacao)
      if (busca && !normalizarTexto(chamado.ClienteNome ?? '').includes(busca)) return false
      if (supervisorID === 'sem-supervisor' && chamado.SupervisorID !== null) return false
      if (supervisorID && supervisorID !== 'sem-supervisor' && chamado.SupervisorID !== supervisorID) return false
      if (status && chamado.Status !== status) return false
      if (categoria && chamado.Categoria !== categoria) return false
      if (inicio && criacao < inicio) return false
      if (fim && criacao > fim) return false
      return true
    })
  }, [buscaCliente, categoria, chamados, dataFinal, dataInicial, status, supervisorID])

  // Restaura a visão completa sem aguardar uma nova requisição.
  function limparFiltros() {
    setBuscaCliente('')
    setSupervisorID('')
    setStatus('')
    setCategoria('')
    setDataInicial('')
    setDataFinal('')
  }

  const possuiFiltro = Boolean(buscaCliente || supervisorID || status || categoria || dataInicial || dataFinal)

  // Estados globais são anunciados de forma acessível antes da renderização da tabela.
  if (carregando) return <p className={styles.info} role="status">Carregando tickets...</p>
  if (erro) return <p className={styles.erro} role="alert">{erro}</p>

  return (
    <div className={styles.pagina}>
      {/* Cabeçalho posiciona a tela no contexto do Gestor e informa o resultado atual. */}
      <header className={styles.cabecalho}>
        <div>
          <span className={styles.sobretitulo}>PAINEL DO GESTOR</span>
          <h1 className={styles.titulo}>Todos os tickets</h1>
          <p className={styles.subtitulo}>Consulte e refine as solicitações registradas{empresaNome ? ` em ${empresaNome}` : ''}.</p>
        </div>
        <span className={styles.total}>{chamadosFiltrados.length} de {chamados.length}</span>
      </header>

      {/* Controles combináveis cobrem exatamente período, supervisor, status, categoria e cliente. */}
      <section className={styles.filtrosPainel} aria-label="Filtros dos tickets">
        <label className={`${styles.campo} ${styles.campoBusca}`}>
          <span>Buscar cliente</span>
          <input
            type="search"
            value={buscaCliente}
            onChange={evento => setBuscaCliente(evento.target.value)}
            placeholder="Digite o nome do cliente"
          />
        </label>

        <label className={styles.campo}>
          <span>Supervisor</span>
          <select value={supervisorID} onChange={evento => setSupervisorID(evento.target.value)}>
            <option value="">Todos</option>
            <option value="sem-supervisor">Sem supervisor</option>
            {supervisores.map(([id, nome]) => <option key={id} value={id}>{nome}</option>)}
          </select>
        </label>

        <label className={styles.campo}>
          <span>Status</span>
          <select value={status} onChange={evento => setStatus(evento.target.value as ChamadoStatus | '')}>
            <option value="">Todos</option>
            {(Object.keys(STATUS_LABEL) as ChamadoStatus[]).map(valor => (
              <option key={valor} value={valor}>{STATUS_LABEL[valor]}</option>
            ))}
          </select>
        </label>

        <label className={styles.campo}>
          <span>Categoria</span>
          <select value={categoria} onChange={evento => setCategoria(evento.target.value)}>
            <option value="">Todas</option>
            {categorias.map(valor => <option key={valor} value={valor}>{valor}</option>)}
          </select>
        </label>

        <label className={styles.campo}>
          <span>De</span>
          <input type="date" value={dataInicial} max={dataFinal || undefined} onChange={evento => setDataInicial(evento.target.value)} />
        </label>

        <label className={styles.campo}>
          <span>Até</span>
          <input type="date" value={dataFinal} min={dataInicial || undefined} onChange={evento => setDataFinal(evento.target.value)} />
        </label>

        <button type="button" className={styles.limpar} onClick={limparFiltros} disabled={!possuiFiltro}>
          Limpar filtros
        </button>
      </section>

      {/* A tabela mantém os fatos centrais legíveis e preserva os IDs usados pelos atalhos do painel. */}
      <section className={styles.tabelaPainel} aria-labelledby="lista-tickets-titulo">
        <div className={styles.tabelaTopo}>
          <div>
            <h2 id="lista-tickets-titulo">Tickets encontrados</h2>
            <p>Resultados em ordem do registro mais recente.</p>
          </div>
          <strong>{chamadosFiltrados.length}</strong>
        </div>

        {chamadosFiltrados.length === 0 ? (
          <div className={styles.vazio}>
            <strong>Nenhum ticket encontrado</strong>
            <span>Ajuste ou limpe os filtros para ampliar a busca.</span>
          </div>
        ) : (
          <div className={styles.tabelaContainer}>
            <table className={styles.tabela}>
              <thead>
                <tr><th>Ticket</th><th>Cliente</th><th>Supervisor</th><th>Status</th><th>Abertura</th></tr>
              </thead>
              <tbody>
                {chamadosFiltrados.map(chamado => (
                  <tr key={chamado.ID} id={`chamado-${chamado.ID}`}>
                    <td>
                      <div className={styles.ticketTitulo}>
                        <span className={styles.prioridadePonto} style={{ background: PRIORIDADE_COR[chamado.Prioridade] }} aria-hidden="true" />
                        <strong>{chamado.Categoria}</strong>
                      </div>
                      <small>{chamado.Fila} · {chamado.Resumo ?? 'Sem resumo informado'}</small>
                    </td>
                    <td>{chamado.ClienteNome ?? 'Cliente não identificado'}</td>
                    <td>{chamado.SupervisorNome ?? 'Não atribuído'}</td>
                    <td><span className={`${styles.status} ${styles[`status--${STATUS_COR[chamado.Status]}`]}`}>{STATUS_LABEL[chamado.Status]}</span></td>
                    <td>{formatarData(chamado.Criacao)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}
