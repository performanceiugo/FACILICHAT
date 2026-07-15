'use client'

// Visao geral do painel do Gestor.
// Combina KPIs calculados pelo backend com distribuicoes derivadas dos chamados do tenant.

import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import Link from 'next/link'
import { api } from '@/lib/api'
import { auth } from '@/lib/auth'
import { useAtualizacaoPeriodica } from '@/lib/useAtualizacaoPeriodica'
import type { Chamado, ChamadoFila, ChamadoPrioridade, ChamadoStatus, DesempenhoSupervisorRelatorio, SupervisorRelatorio, VisaoGeralRelatorio } from '@/types'
import styles from './visao-geral.module.css'

// Ordem canonica dos status do MVP, usada para manter os graficos estaveis mesmo com zero itens.
const STATUS_ORDEM: ChamadoStatus[] = ['Recebido', 'EmAndamento', 'Agendado', 'Concluido', 'Cancelado']

// Labels de status em linguagem de interface, sem expor nomes tecnicos do enum.
const STATUS_LABEL: Record<ChamadoStatus, string> = {
  Recebido: 'Recebido',
  EmAndamento: 'Em andamento',
  Agendado: 'Agendado',
  Concluido: 'Concluido',
  Cancelado: 'Cancelado',
}

// Ordem das filas atuais para a leitura do volume operacional por area.
const FILA_ORDEM: ChamadoFila[] = ['Operacional', 'RH', 'Financeiro', 'Comercial']

// Peso visual da prioridade para ordenar o painel de atencao sem inventar SLA.
const PRIORIDADE_PESO: Record<ChamadoPrioridade, number> = {
  Critica: 4,
  Alta: 3,
  Media: 2,
  Baixa: 1,
}

// Tipos exibidos no painel; oportunidade significa fila Comercial já roteada, não inferência de IA.
type AlertaTipo = 'critico' | 'atencao' | 'oportunidade'

// Classifica cada chamado aberto sem fabricar SLA ou intenção comercial além da fila persistida.
function classificarAlerta(chamado: Chamado): { tipo: AlertaTipo; rotulo: string } {
  if (chamado.Prioridade === 'Critica') return { tipo: 'critico', rotulo: 'Crítico' }
  if (chamado.Fila === 'Comercial') return { tipo: 'oportunidade', rotulo: 'Oportunidade' }
  return { tipo: 'atencao', rotulo: 'Atenção' }
}

// Status finais saem da fila ativa e nao entram nos alertas de atencao.
const STATUS_FINAIS = new Set<ChamadoStatus>(['Concluido', 'Cancelado'])

// Conta ocorrencias de um campo textual preservando tipagem dos enums.
function contarPorCampo<T extends string>(itens: Chamado[], obterCampo: (chamado: Chamado) => T): Record<T, number> {
  return itens.reduce((acc, chamado) => {
    const chave = obterCampo(chamado)
    acc[chave] = (acc[chave] ?? 0) + 1
    return acc
  }, {} as Record<T, number>)
}

// Calcula ha quantos dias um chamado foi aberto para dar contexto ao painel de atencao.
function diasDesde(dataIso: string): number {
  const data = new Date(dataIso).getTime()
  const diferenca = Date.now() - data
  if (!Number.isFinite(diferenca)) return 0
  return Math.max(0, Math.floor(diferenca / (1000 * 60 * 60 * 24)))
}

// Formata duracoes executivas sem inventar valor quando o backend nao possui amostra.
function formatarDuracao(minutos: number | null): string {
  if (minutos === null) return '—'
  if (minutos < 60) return `${Math.round(minutos)} min`

  const horas = minutos / 60
  return `${horas.toLocaleString('pt-BR', { maximumFractionDigits: 1 })} h`
}

export default function VisaoGeralPage() {
  const [chamados, setChamados] = useState<Chamado[]>([])
  const [relatorio, setRelatorio] = useState<VisaoGeralRelatorio | null>(null)
  const [supervisores, setSupervisores] = useState<SupervisorRelatorio[]>([])
  const [desempenhos, setDesempenhos] = useState<DesempenhoSupervisorRelatorio[]>([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState('')
  const [empresaNome, setEmpresaNome] = useState<string | null>(null)
  const ativoRef = useRef(true)

  // Busca KPIs e chamados juntos. `mostrarCarregando` so vale true na carga inicial; o polling
  // troca os dados em silencio e preserva a ultima leitura boa se uma atualizacao falhar.
  const buscarVisaoGeral = useCallback((mostrarCarregando: boolean) => {
    if (mostrarCarregando) setCarregando(true)
    Promise.all([
      api.relatorios.visaoGeral(),
      api.chamados.listar(),
      api.relatorios.supervisores(),
      api.relatorios.desempenhoSupervisores(),
    ])
      .then(([novoRelatorio, novosChamados, novosSupervisores, novosDesempenhos]) => {
        if (!ativoRef.current) return
        setRelatorio(novoRelatorio)
        setChamados(novosChamados)
        setSupervisores(novosSupervisores)
        setDesempenhos(novosDesempenhos)
        if (mostrarCarregando) setErro('')
      })
      .catch(err => {
        if (ativoRef.current && mostrarCarregando) {
          setErro(err instanceof Error ? err.message : 'Nao foi possivel carregar a visao geral.')
        }
      })
      .finally(() => {
        if (ativoRef.current && mostrarCarregando) setCarregando(false)
      })
  }, [])

  // Carrega a Empresa de exibicao e a lista de chamados ao montar a tela.
  useEffect(() => {
    ativoRef.current = true
    setEmpresaNome(auth.empresaNome())
    buscarVisaoGeral(true)
    return () => { ativoRef.current = false }
  }, [buscarVisaoGeral])

  useAtualizacaoPeriodica(() => buscarVisaoGeral(false))

  // Agrega os chamados em estruturas de exibicao para KPIs, graficos e atencoes.
  const resumo = useMemo(() => {
    const chamadosAbertos = chamados.filter(chamado => !STATUS_FINAIS.has(chamado.Status))
    const statusContagem = contarPorCampo(chamados, chamado => chamado.Status)
    const filaContagem = contarPorCampo(chamados, chamado => chamado.Fila)
    const categoriaContagem = contarPorCampo(chamados, chamado => chamado.Categoria || 'Sem categoria')
    const maxStatus = Math.max(1, ...STATUS_ORDEM.map(status => statusContagem[status] ?? 0))
    const maxFila = Math.max(1, ...FILA_ORDEM.map(fila => filaContagem[fila] ?? 0))

    return {
      statusContagem,
      filaContagem,
      categoriaRanking: Object.entries(categoriaContagem)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 6),
      maxStatus,
      maxFila,
      atencoes: chamadosAbertos
        .filter(chamado => chamado.Fila === 'Comercial' || ['Alta', 'Critica'].includes(chamado.Prioridade) || chamado.Status === 'Recebido')
        .sort((a, b) => {
          // Críticos ficam no topo; depois atenção operacional e, então, sinais comerciais.
          const tipoPeso: Record<AlertaTipo, number> = { critico: 3, atencao: 2, oportunidade: 1 }
          const tipo = tipoPeso[classificarAlerta(b).tipo] - tipoPeso[classificarAlerta(a).tipo]
          if (tipo !== 0) return tipo
          const prioridade = PRIORIDADE_PESO[b.Prioridade] - PRIORIDADE_PESO[a.Prioridade]
          if (prioridade !== 0) return prioridade
          return new Date(a.Criacao).getTime() - new Date(b.Criacao).getTime()
        })
        .slice(0, 5),
    }
  }, [chamados])

  // KPIs principais usam exclusivamente o relatorio real; nulos aparecem como travessao.
  const kpis = [
    { label: 'Chamados abertos', valor: relatorio?.TotalAbertos ?? '—', detalhe: 'Em operacao agora', tom: 'info' },
    { label: 'SLA estourado', valor: relatorio?.SlaEstourado ?? '—', detalhe: 'Prazo vencido', tom: 'danger' },
    { label: '1ª resposta media', valor: formatarDuracao(relatorio?.PrimeiraRespostaMediaMinutos ?? null), detalhe: 'Ate o primeiro retorno', tom: 'warning' },
    { label: 'Resolucao media', valor: formatarDuracao(relatorio?.ResolucaoMediaMinutos ?? null), detalhe: 'Chamados concluidos', tom: 'success' },
  ] as const

  // Junta os dois contratos por ID para exibir carga, resposta e estado com lastro operacional.
  const desempenhoPorSupervisor = supervisores.map(supervisor => {
    const desempenho = desempenhos.find(item => item.ID === supervisor.ID)
    const estado = (desempenho?.Parados ?? 0) > 0
      ? 'Precisa de atenção'
      : supervisor.Abertos === 0
        ? 'Sem fila aberta'
        : 'Em dia'
    const tom = (desempenho?.Parados ?? 0) > 0 ? 'atencao' : supervisor.Abertos === 0 ? 'neutro' : 'sucesso'
    return { ...supervisor, desempenho, estado, tom }
  })

  // Item B5: role="status"/"alert" dão aria-live implícito aos estados de carga e erro
  if (carregando) return <p className={styles.info} role="status">Carregando visao geral...</p>
  if (erro) return <p className={styles.erro} role="alert">{erro}</p>

  return (
    <div className={styles.pagina}>
      {/* Cabecalho executivo: contexto do tenant e atalho para a fila detalhada. */}
      <header className={styles.cabecalho}>
        <div>
          <p className={styles.etiqueta}>Painel do Gestor</p>
          <h1 className={styles.titulo}>Visao geral</h1>
          <p className={styles.subtitulo}>
            {empresaNome ? `${empresaNome} - chamados, filas e prioridades em uma leitura unica.` : 'Chamados, filas e prioridades em uma leitura unica.'}
          </p>
        </div>
        <Link href="/painel/chamados" className={styles.acaoSecundaria}>
          Ver chamados
        </Link>
      </header>

      {/* Cartoes de KPI: leitura rapida do volume e do que pede acao. */}
      <section className={styles.kpis} aria-label="Indicadores principais">
        {kpis.map(kpi => (
          <article key={kpi.label} className={`${styles.kpi} ${styles[`kpi--${kpi.tom}`]}`}>
            <span className={styles.kpiLabel}>{kpi.label}</span>
            <strong className={styles.kpiValor}>{kpi.valor}</strong>
            <span className={styles.kpiDetalhe}>{kpi.detalhe}</span>
          </article>
        ))}
      </section>

      {/* Linha principal: primeiro o que exige atencao, depois tendencia operacional. */}
      <section className={styles.gradePrincipal}>
        <article id="atencao" className={styles.painelAtencao}>
          <div className={styles.secaoTopo}>
            <div>
              <h2 className={styles.secaoTitulo}>O que precisa da sua atencao</h2>
              <p className={styles.secaoDescricao}>Críticos, atenções operacionais e oportunidades já encaminhadas ao Comercial.</p>
            </div>
          </div>

          {resumo.atencoes.length === 0 ? (
            <p className={styles.vazio}>Nada urgente na fila agora.</p>
          ) : (
            <div className={styles.listaAtencao}>
              {resumo.atencoes.map(chamado => {
                const alerta = classificarAlerta(chamado)
                return (
                <Link key={chamado.ID} href={`/painel/chamados#chamado-${chamado.ID}`} className={styles.itemAtencao}>
                  <span className={`${styles.prioridade} ${styles[`prioridade--${alerta.tipo}`]}`}>
                    {alerta.rotulo}
                  </span>
                  <div className={styles.atencaoConteudo}>
                    <strong>{chamado.Categoria}</strong>
                    <span>{chamado.Resumo ?? 'Chamado sem resumo informado.'}</span>
                  </div>
                  <span className={styles.atencaoMeta}>{diasDesde(chamado.Criacao)}d</span>
                  <span className={styles.atalhoChamado}>Abrir chamado →</span>
                </Link>
                )
              })}
            </div>
          )}
        </article>

        <article className={styles.painelGrafico}>
          <div className={styles.secaoTopo}>
            <div>
              <h2 className={styles.secaoTitulo}>Fluxo por status</h2>
              <p className={styles.secaoDescricao}>Distribuicao atual dos tickets carregados.</p>
            </div>
          </div>

          <div className={styles.barrasStatus}>
            {STATUS_ORDEM.map(status => {
              const total = resumo.statusContagem[status] ?? 0
              const altura = `${Math.max(6, (total / resumo.maxStatus) * 100)}%`
              return (
                <div key={status} className={styles.statusColuna}>
                  <div className={styles.statusTrilho}>
                    <span className={`${styles.statusBarra} ${styles[`statusBarra--${status}`]}`} style={{ height: altura }} />
                  </div>
                  <strong>{total}</strong>
                  <span>{STATUS_LABEL[status]}</span>
                </div>
              )
            })}
          </div>
        </article>
      </section>

      {/* Linha secundaria: tendencia por fila e categorias vindas dos dados reais. */}
      <section className={styles.gradeSecundaria}>
        <article className={styles.painelLista}>
          <h2 className={styles.secaoTitulo}>Volume por fila</h2>
          <div className={styles.listaBarras}>
            {FILA_ORDEM.map(fila => {
              const total = resumo.filaContagem[fila] ?? 0
              const largura = `${(total / resumo.maxFila) * 100}%`
              return (
                <div key={fila} className={styles.linhaBarra}>
                  <div className={styles.linhaBarraTopo}>
                    <span>{fila}</span>
                    <strong>{total}</strong>
                  </div>
                  <span className={styles.trilhoHorizontal}>
                    <span className={styles.barraHorizontal} style={{ width: largura }} />
                  </span>
                </div>
              )
            })}
          </div>
        </article>

        <article className={styles.painelLista}>
          <h2 className={styles.secaoTitulo}>Volume por categoria</h2>
          {resumo.categoriaRanking.length === 0 ? (
            <p className={styles.vazio}>Sem categorias para exibir.</p>
          ) : (
            <div className={styles.categorias}>
              {resumo.categoriaRanking.map(([categoria, total]) => (
                <div key={categoria} className={styles.categoriaLinha}>
                  <span>{categoria}</span>
                  <strong>{total}</strong>
                </div>
              ))}
            </div>
          )}
        </article>
      </section>

      {/* Desempenho cruza carga/resposta com fechamentos e gargalos reais por supervisor. */}
      <section className={styles.painelDesempenho} aria-labelledby="desempenho-supervisores-titulo">
        <div className={styles.secaoTopo}>
          <div>
            <h2 id="desempenho-supervisores-titulo" className={styles.secaoTitulo}>Desempenho por supervisor</h2>
            <p className={styles.secaoDescricao}>Carga, primeira resposta e estado derivados da operação registrada.</p>
          </div>
          <Link href="/painel/supervisores" className={styles.linkDetalhe}>Ver equipe</Link>
        </div>

        {desempenhoPorSupervisor.length === 0 ? (
          <p className={styles.vazio}>Nenhum supervisor cadastrado.</p>
        ) : (
          <div className={styles.tabelaContainer}>
            <table className={styles.tabelaDesempenho}>
              <thead><tr><th>Supervisor</th><th>Abertos</th><th>1ª resposta</th><th>Estado</th></tr></thead>
              <tbody>
                {desempenhoPorSupervisor.map(supervisor => (
                  <tr key={supervisor.ID}>
                    <td>
                      <strong>{supervisor.Nome}</strong>
                      <small>{supervisor.desempenho?.Resolvidos ?? 0} de {supervisor.desempenho?.Recebidos ?? 0} resolvidos</small>
                    </td>
                    <td>{supervisor.Abertos}</td>
                    <td>{formatarDuracao(supervisor.PrimeiraRespostaMediaMinutos)}</td>
                    <td><span className={`${styles.estadoSupervisor} ${styles[`estadoSupervisor--${supervisor.tom}`]}`}>{supervisor.estado}</span></td>
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
