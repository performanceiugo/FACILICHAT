'use client'

// Página de supervisores do painel do Gestor.
// O layout já representa a experiência final, mas mantém um estado de integração honesto
// enquanto o endpoint de métricas por supervisor (item 868k60w1e) não está disponível.

import { useState } from 'react'
import Link from 'next/link'
import styles from './supervisores.module.css'

// Contrato visual esperado do relatório; será movido para os tipos globais quando o backend existir.
interface SupervisorResumo {
  ID: string
  Nome: string
  Abertos: number
  Atrasados: number
  PrimeiraRespostaMinutos: number | null
  Chamados: SupervisorChamadoResumo[]
}

// Recorte mínimo de um chamado exibido ao expandir o card de um supervisor.
interface SupervisorChamadoResumo {
  ID: string
  Categoria: string
  Resumo: string | null
  Prioridade: 'Baixa' | 'Media' | 'Alta' | 'Critica'
  Status: 'Recebido' | 'EmAndamento' | 'Agendado' | 'Concluido' | 'Cancelado'
}

// A lista permanece vazia até que o item de backend 868k60w1e forneça dados reais do tenant.
// Não usamos fixtures: a demonstração visual não pode ser confundida com informação operacional.
const SUPERVISORES: SupervisorResumo[] = []

// Gera iniciais neutras para o avatar usando somente o nome retornado pelo backend.
function obterIniciais(nome: string): string {
  return nome
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map(parte => parte[0]?.toUpperCase() ?? '')
    .join('') || '?'
}

// Formata a métrica de primeira resposta sem fabricar um valor quando não houver lastro.
function formatarPrimeiraResposta(minutos: number | null): string {
  return minutos === null ? '—' : `${minutos} min`
}

export default function SupervisoresPage() {
  // Guarda qual card está expandido; clicar novamente recolhe a fila daquele supervisor.
  const [supervisorAbertoID, setSupervisorAbertoID] = useState<string | null>(null)

  // Alterna a expansão sem navegar para uma rota que ainda depende do filtro do backend.
  function alternarSupervisor(supervisorID: string) {
    setSupervisorAbertoID(atual => atual === supervisorID ? null : supervisorID)
  }

  return (
    <div className={styles.pagina}>
      {/* Cabeçalho apresenta a finalidade operacional da tela sem prometer tempo real. */}
      <header className={styles.cabecalho}>
        <div>
          <p className={styles.etiqueta}>Operação</p>
          <h1 className={styles.titulo}>Supervisores</h1>
          <p className={styles.subtitulo}>
            Compare a carga da equipe e abra a fila de cada supervisor em um só lugar.
          </p>
        </div>
        <Link href="/painel/chamados" className={styles.acaoSecundaria}>
          Ver todos os chamados
        </Link>
      </header>

      {/* Resumo mantém a hierarquia da tela final; travessões indicam métricas ainda sem fonte. */}
      <section className={styles.resumo} aria-label="Resumo da supervisão">
        <article className={styles.resumoItem}>
          <span>Supervisores ativos</span>
          <strong>—</strong>
          <small>Aguardando integração</small>
        </article>
        <article className={styles.resumoItem}>
          <span>Chamados atribuídos</span>
          <strong>—</strong>
          <small>Aguardando integração</small>
        </article>
        <article className={`${styles.resumoItem} ${styles.resumoAtencao}`}>
          <span>Precisam de atenção</span>
          <strong>—</strong>
          <small>Aguardando integração</small>
        </article>
      </section>

      {/* Cards reais serão renderizados assim que o relatório por supervisor estiver disponível. */}
      {SUPERVISORES.length > 0 ? (
        <section className={styles.grade} aria-label="Lista de supervisores">
          {SUPERVISORES.map(supervisor => {
            const aberto = supervisorAbertoID === supervisor.ID
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
                    <strong>{supervisor.Nome}</strong>
                    <small>Ver fila do supervisor</small>
                  </span>
                  <span className={styles.metricas}>
                    <span><strong>{supervisor.Abertos}</strong><small>abertos</small></span>
                    <span className={supervisor.Atrasados > 0 ? styles.metricaCritica : undefined}>
                      <strong>{supervisor.Atrasados}</strong><small>atrasados</small>
                    </span>
                    <span><strong>{formatarPrimeiraResposta(supervisor.PrimeiraRespostaMinutos)}</strong><small>1ª resposta</small></span>
                  </span>
                  <span className={styles.chevron} aria-hidden="true">{aberto ? '−' : '+'}</span>
                </button>

                {aberto && (
                  <div id={`fila-supervisor-${supervisor.ID}`} className={styles.fila}>
                    {supervisor.Chamados.length === 0 ? (
                      <p className={styles.filaVazia}>Nenhum chamado aberto para este supervisor.</p>
                    ) : (
                      supervisor.Chamados.map(chamado => (
                        <div key={chamado.ID} className={styles.chamado}>
                          <div>
                            <strong>{chamado.Categoria}</strong>
                            <span>{chamado.Resumo ?? 'Chamado sem resumo informado.'}</span>
                          </div>
                          <span className={styles.chamadoMeta}>{chamado.Prioridade} · {chamado.Status}</span>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </article>
            )
          })}
        </section>
      ) : (
        <section className={styles.integracao} aria-labelledby="integracao-titulo">
          {/* Prévia sem dados mostra a anatomia dos cards sem simular pessoas ou indicadores. */}
          <div className={styles.preview} aria-hidden="true">
            {[0, 1, 2].map(indice => (
              <div key={indice} className={styles.previewCard}>
                <span className={styles.previewAvatar} />
                <span className={styles.previewTexto}>
                  <span />
                  <span />
                </span>
                <span className={styles.previewMetricas}>
                  <span /><span /><span />
                </span>
              </div>
            ))}
          </div>
          <div className={styles.integracaoMensagem}>
            <span className={styles.integracaoIcone} aria-hidden="true">↻</span>
            <div>
              <h2 id="integracao-titulo">Dados da equipe em preparação</h2>
              <p>
                A página está pronta para receber supervisores, carga, atrasos e primeira resposta
                assim que o relatório da operação for conectado.
              </p>
            </div>
          </div>
        </section>
      )}
    </div>
  )
}
