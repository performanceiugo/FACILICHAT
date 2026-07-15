'use client'

// Página de supervisores do painel do Gestor.
// Compara métricas reais da equipe e busca a fila individual somente ao expandir um card.

import { useCallback, useEffect, useRef, useState } from 'react'
import Link from 'next/link'
import { api } from '@/lib/api'
import { useAtualizacaoPeriodica } from '@/lib/useAtualizacaoPeriodica'
import type { Chamado, SupervisorRelatorio } from '@/types'
import styles from './supervisores.module.css'

// Gera iniciais neutras para o avatar usando somente o nome retornado pelo backend.
function obterIniciais(nome: string): string {
  return nome
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map(parte => parte[0]?.toUpperCase() ?? '')
    .join('') || '?'
}

// Formata a média sem fabricar um valor quando não houver resposta registrada.
function formatarPrimeiraResposta(minutos: number | null): string {
  return minutos === null ? '—' : `${minutos} min`
}

// Traduz valores técnicos do status para a linguagem exibida no painel.
function formatarStatus(status: Chamado['Status']): string {
  const rotulos: Record<Chamado['Status'], string> = {
    Recebido: 'Recebido',
    EmAndamento: 'Em andamento',
    Agendado: 'Agendado',
    Concluido: 'Concluído',
    Cancelado: 'Cancelado',
  }
  return rotulos[status]
}

export default function SupervisoresPage() {
  // Estado principal conserva a última leitura boa durante atualizações automáticas silenciosas.
  const [supervisores, setSupervisores] = useState<SupervisorRelatorio[]>([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState('')
  const ativoRef = useRef(true)
  const cargaInicialConcluidaRef = useRef(false)

  // Filas são armazenadas por supervisor para não refazer a chamada ao recolher e reabrir o card.
  const [supervisorAbertoID, setSupervisorAbertoID] = useState<string | null>(null)
  const [filas, setFilas] = useState<Record<string, Chamado[]>>({})
  const [filasCarregando, setFilasCarregando] = useState<Record<string, boolean>>({})
  const [errosFila, setErrosFila] = useState<Record<string, string>>({})

  // Busca métricas iniciais e atualizações periódicas sem apagar dados bons quando uma falhar.
  const buscarSupervisores = useCallback(async () => {
    try {
      const dados = await api.relatorios.supervisores()
      if (!ativoRef.current) return
      setSupervisores(dados)
      setErro('')
    } catch (e) {
      if (ativoRef.current && !cargaInicialConcluidaRef.current) {
        setErro(e instanceof Error ? e.message : 'Não foi possível carregar os supervisores.')
      }
    } finally {
      if (ativoRef.current) {
        cargaInicialConcluidaRef.current = true
        setCarregando(false)
      }
    }
  }, [])

  useEffect(() => {
    ativoRef.current = true
    buscarSupervisores()
    return () => { ativoRef.current = false }
  }, [buscarSupervisores])

  useAtualizacaoPeriodica(buscarSupervisores)

  // Carrega a fila real na primeira abertura; tentativas com erro podem ser refeitas ao clicar.
  async function carregarFila(supervisorID: string) {
    setFilasCarregando(atual => ({ ...atual, [supervisorID]: true }))
    setErrosFila(atual => ({ ...atual, [supervisorID]: '' }))
    try {
      const chamados = await api.chamados.listarPorSupervisor(supervisorID)
      if (ativoRef.current) setFilas(atual => ({ ...atual, [supervisorID]: chamados }))
    } catch (e) {
      if (ativoRef.current) {
        setErrosFila(atual => ({
          ...atual,
          [supervisorID]: e instanceof Error ? e.message : 'Não foi possível carregar esta fila.',
        }))
      }
    } finally {
      if (ativoRef.current) setFilasCarregando(atual => ({ ...atual, [supervisorID]: false }))
    }
  }

  // Alterna o card e dispara a busca sob demanda quando a fila ainda não está em cache.
  function alternarSupervisor(supervisorID: string) {
    if (supervisorAbertoID === supervisorID) {
      setSupervisorAbertoID(null)
      return
    }
    setSupervisorAbertoID(supervisorID)
    if (!filas[supervisorID] || errosFila[supervisorID]) carregarFila(supervisorID)
  }

  // Indicadores de topo são somas transparentes das métricas retornadas pelo relatório.
  const totalAbertos = supervisores.reduce((total, supervisor) => total + supervisor.Abertos, 0)
  const totalAtrasados = supervisores.reduce((total, supervisor) => total + supervisor.Atrasados, 0)

  return (
    <div className={styles.pagina}>
      {/* Cabeçalho apresenta a finalidade operacional e o acesso à lista geral. */}
      <header className={styles.cabecalho}>
        <div>
          <p className={styles.etiqueta}>Operação</p>
          <h1 className={styles.titulo}>Supervisores</h1>
          <p className={styles.subtitulo}>
            Compare a carga da equipe e abra a fila de cada supervisor em um só lugar.
          </p>
        </div>
        <Link href="/painel/chamados" className={styles.acaoSecundaria}>Ver todos os chamados</Link>
      </header>

      {/* Resumo usa somente contagens reais da Empresa autenticada. */}
      <section className={styles.resumo} aria-label="Resumo da supervisão">
        <article className={styles.resumoItem}>
          <span>Supervisores</span><strong>{carregando ? '—' : supervisores.length}</strong>
          <small>Na equipe cadastrada</small>
        </article>
        <article className={styles.resumoItem}>
          <span>Chamados atribuídos</span><strong>{carregando ? '—' : totalAbertos}</strong>
          <small>Em filas abertas</small>
        </article>
        <article className={`${styles.resumoItem} ${styles.resumoAtencao}`}>
          <span>Precisam de atenção</span><strong>{carregando ? '—' : totalAtrasados}</strong>
          <small>Com SLA atrasado</small>
        </article>
      </section>

      {carregando && <p className={styles.estado} role="status">Carregando supervisores...</p>}
      {!carregando && erro && <p className={styles.estadoErro} role="alert">{erro}</p>}
      {!carregando && !erro && supervisores.length === 0 && (
        <section className={styles.estadoVazio}>
          <h2>Nenhum supervisor cadastrado</h2>
          <p>Quando a equipe for cadastrada, a carga operacional aparecerá aqui.</p>
        </section>
      )}

      {/* Cada card abre sua fila real sem bloquear ou recarregar a página inteira. */}
      {!carregando && !erro && supervisores.length > 0 && (
        <section className={styles.grade} aria-label="Lista de supervisores">
          {supervisores.map(supervisor => {
            const aberto = supervisorAbertoID === supervisor.ID
            const fila = filas[supervisor.ID]
            return (
              <article key={supervisor.ID} className={styles.card}>
                <button
                  type="button"
                  className={styles.cardBotao}
                  onClick={() => alternarSupervisor(supervisor.ID)}
                  aria-expanded={aberto}
                  aria-controls={`fila-supervisor-${supervisor.ID}`}
                >
                  <span className={styles.avatar}>{obterIniciais(supervisor.Nome)}</span>
                  <span className={styles.identidade}>
                    <strong>{supervisor.Nome}</strong><small>Ver fila do supervisor</small>
                  </span>
                  <span className={styles.metricas}>
                    <span><strong>{supervisor.Abertos}</strong><small>abertos</small></span>
                    <span className={supervisor.Atrasados > 0 ? styles.metricaCritica : undefined}>
                      <strong>{supervisor.Atrasados}</strong><small>atrasados</small>
                    </span>
                    <span>
                      <strong>{formatarPrimeiraResposta(supervisor.PrimeiraRespostaMediaMinutos)}</strong>
                      <small>1ª resposta</small>
                    </span>
                  </span>
                  <span className={styles.chevron} aria-hidden="true">{aberto ? '−' : '+'}</span>
                </button>

                {aberto && (
                  <div id={`fila-supervisor-${supervisor.ID}`} className={styles.fila}>
                    {filasCarregando[supervisor.ID] && <p className={styles.filaVazia} role="status">Carregando fila...</p>}
                    {errosFila[supervisor.ID] && (
                      <div className={styles.filaErro} role="alert">
                        <span>{errosFila[supervisor.ID]}</span>
                        <button type="button" onClick={() => carregarFila(supervisor.ID)}>Tentar novamente</button>
                      </div>
                    )}
                    {!filasCarregando[supervisor.ID] && !errosFila[supervisor.ID] && fila?.length === 0 && (
                      <p className={styles.filaVazia}>Nenhum chamado atribuído a este supervisor.</p>
                    )}
                    {!filasCarregando[supervisor.ID] && !errosFila[supervisor.ID] && fila?.map(chamado => (
                      <div key={chamado.ID} className={styles.chamado}>
                        <div><strong>{chamado.Categoria}</strong><span>{chamado.Resumo ?? 'Chamado sem resumo informado.'}</span></div>
                        <span className={styles.chamadoMeta}>{chamado.Prioridade} · {formatarStatus(chamado.Status)}</span>
                      </div>
                    ))}
                  </div>
                )}
              </article>
            )
          })}
        </section>
      )}
    </div>
  )
}
