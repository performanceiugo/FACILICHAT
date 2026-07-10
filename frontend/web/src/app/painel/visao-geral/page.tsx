'use client'

// Visao geral do painel do Gestor.
// Este recorte visual usa apenas os chamados ja disponiveis para mostrar a direcao do produto
// sem depender dos endpoints de relatorio da Fase 4 que ainda serao implementados no backend.

import { useEffect, useMemo, useState } from 'react'
import Link from 'next/link'
import { api } from '@/lib/api'
import { auth } from '@/lib/auth'
import type { Chamado, ChamadoFila, ChamadoPrioridade, ChamadoStatus } from '@/types'
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

// Classe semantica de cada prioridade, ancorada nos tokens de feedback do design system.
const PRIORIDADE_TOM: Record<ChamadoPrioridade, 'critico' | 'atencao' | 'neutro' | 'sucesso'> = {
  Critica: 'critico',
  Alta: 'atencao',
  Media: 'neutro',
  Baixa: 'sucesso',
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

export default function VisaoGeralPage() {
  const [chamados, setChamados] = useState<Chamado[]>([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState('')
  const [empresaNome, setEmpresaNome] = useState<string | null>(null)

  // Carrega a Empresa de exibicao e a lista de chamados ao montar a tela.
  useEffect(() => {
    let ativo = true
    setEmpresaNome(auth.empresaNome())
    api.chamados.listar()
      .then(resultado => {
        if (ativo) setChamados(resultado)
      })
      .catch(err => {
        if (ativo) setErro(err instanceof Error ? err.message : 'Nao foi possivel carregar a visao geral.')
      })
      .finally(() => {
        if (ativo) setCarregando(false)
      })
    return () => { ativo = false }
  }, [])

  // Agrega os chamados em estruturas de exibicao para KPIs, graficos e atencoes.
  const resumo = useMemo(() => {
    const chamadosAbertos = chamados.filter(chamado => !STATUS_FINAIS.has(chamado.Status))
    const chamadosCriticos = chamadosAbertos.filter(chamado => chamado.Prioridade === 'Critica')
    const chamadosAltaOuCritica = chamadosAbertos.filter(chamado => ['Alta', 'Critica'].includes(chamado.Prioridade))
    const statusContagem = contarPorCampo(chamados, chamado => chamado.Status)
    const filaContagem = contarPorCampo(chamados, chamado => chamado.Fila)
    const categoriaContagem = contarPorCampo(chamados, chamado => chamado.Categoria || 'Sem categoria')
    const maxStatus = Math.max(1, ...STATUS_ORDEM.map(status => statusContagem[status] ?? 0))
    const maxFila = Math.max(1, ...FILA_ORDEM.map(fila => filaContagem[fila] ?? 0))

    return {
      chamadosAbertos,
      chamadosCriticos,
      chamadosAltaOuCritica,
      statusContagem,
      filaContagem,
      categoriaRanking: Object.entries(categoriaContagem)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 6),
      maxStatus,
      maxFila,
      atencoes: chamadosAbertos
        .filter(chamado => ['Alta', 'Critica'].includes(chamado.Prioridade) || chamado.Status === 'Recebido')
        .sort((a, b) => {
          const prioridade = PRIORIDADE_PESO[b.Prioridade] - PRIORIDADE_PESO[a.Prioridade]
          if (prioridade !== 0) return prioridade
          return new Date(a.Criacao).getTime() - new Date(b.Criacao).getTime()
        })
        .slice(0, 5),
    }
  }, [chamados])

  // KPIs principais: somente metricas derivaveis hoje, sem simular SLA ou tempos medios inexistentes.
  const kpis = [
    { label: 'Chamados abertos', valor: resumo.chamadosAbertos.length, detalhe: 'Em operacao agora', tom: 'info' },
    { label: 'Atencao imediata', valor: resumo.chamadosAltaOuCritica.length, detalhe: 'Alta ou critica abertas', tom: 'danger' },
    { label: 'Criticos', valor: resumo.chamadosCriticos.length, detalhe: 'Prioridade maxima', tom: 'warning' },
    { label: 'Concluidos', valor: resumo.statusContagem.Concluido ?? 0, detalhe: 'Base carregada', tom: 'success' },
  ] as const

  if (carregando) return <p className={styles.info}>Carregando visao geral...</p>
  if (erro) return <p className={styles.erro}>{erro}</p>

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
        <article className={styles.painelAtencao}>
          <div className={styles.secaoTopo}>
            <div>
              <h2 className={styles.secaoTitulo}>O que precisa da sua atencao</h2>
              <p className={styles.secaoDescricao}>Chamados abertos com prioridade alta, critica ou ainda recebidos.</p>
            </div>
          </div>

          {resumo.atencoes.length === 0 ? (
            <p className={styles.vazio}>Nada urgente na fila agora.</p>
          ) : (
            <div className={styles.listaAtencao}>
              {resumo.atencoes.map(chamado => (
                <div key={chamado.ID} className={styles.itemAtencao}>
                  <span className={`${styles.prioridade} ${styles[`prioridade--${PRIORIDADE_TOM[chamado.Prioridade]}`]}`}>
                    {chamado.Prioridade}
                  </span>
                  <div className={styles.atencaoConteudo}>
                    <strong>{chamado.Categoria}</strong>
                    <span>{chamado.Resumo ?? 'Chamado sem resumo informado.'}</span>
                  </div>
                  <span className={styles.atencaoMeta}>{diasDesde(chamado.Criacao)}d</span>
                </div>
              ))}
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
    </div>
  )
}
