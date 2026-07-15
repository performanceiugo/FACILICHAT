'use client'

// Página de listagem de chamados do painel web
// Gestores e supervisores veem todos os chamados; clientes veem apenas os seus (filtro no backend)

import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '@/lib/api'
import { auth } from '@/lib/auth'
import { useAtualizacaoPeriodica } from '@/lib/useAtualizacaoPeriodica'
import type { Chamado, ChamadoPrioridade, ChamadoStatus } from '@/types'
import styles from './chamados.module.css'

// Labels amigáveis para exibição dos status no card.
// Tipar com os enums (item M7) faz o compilador cobrar esta tabela quando um status novo
// entrar em `ChamadoStatus` — com `Record<string, string>` um valor faltante só aparecia
// em runtime, como badge sem texto.
const STATUS_LABEL: Record<ChamadoStatus, string> = {
  Recebido: 'Recebido',
  EmAndamento: 'Em Andamento',
  Agendado: 'Agendado',
  Concluido: 'Concluído',
  Cancelado: 'Cancelado',
}

// Classe de cor do badge de status — semântica do design system (pílula bg+texto).
// Recebido fica neutro (só chegou); Em andamento usa âmbar (atenção); Agendado usa azul
// (compromisso confirmado); Concluído usa verde; Cancelado fica neutro-esmaecido.
const STATUS_COR: Record<ChamadoStatus, string> = {
  Recebido: 'neutro',
  EmAndamento: 'atencao',
  Agendado: 'info',
  Concluido: 'sucesso',
  Cancelado: 'apagado',
}

// Cores de destaque para cada nível de prioridade — tokens do design system.
// "Crítica" não tem roxo no DS: usa o vermelho mais intenso (danger-700) para se
// distinguir de "Alta" (danger-500) mantendo-se dentro da paleta da marca.
const PRIORIDADE_COR: Record<ChamadoPrioridade, string> = {
  Baixa: 'var(--success-500)',  // verde
  Media: 'var(--warning-500)',  // âmbar
  Alta: 'var(--danger-500)',    // vermelho
  Critica: 'var(--danger-700)', // vermelho intenso
}

export default function ChamadosPage() {
  const [chamados, setChamados] = useState<Chamado[]>([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState('')
  const [empresaNome, setEmpresaNome] = useState<string | null>(null)
  const montadoRef = useRef(true)

  // Busca os chamados. `mostrarCarregando` so vale true na carga inicial — a atualizacao
  // automatica em segundo plano (useAtualizacaoPeriodica) troca a lista sem piscar loading nem
  // erro, mantendo a ultima lista boa na tela se uma atualizacao falhar.
  const buscarChamados = useCallback((mostrarCarregando: boolean) => {
    if (mostrarCarregando) setCarregando(true)
    api.chamados.listar()
      .then(lista => {
        if (!montadoRef.current) return
        setChamados(lista)
        if (mostrarCarregando) setErro('')
      })
      .catch((err: unknown) => {
        // Narrowing explícito (item M7): sem o instanceof, um throw não-Error viraria undefined na tela
        if (montadoRef.current && mostrarCarregando) {
          setErro(err instanceof Error ? err.message : 'Não foi possível carregar os chamados.')
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

  // Item B5: role="status" (aria-live polite) anuncia o carregamento a leitores de tela;
  // role="alert" (aria-live assertive) anuncia o erro imediatamente
  if (carregando) return <p className={styles.info} role="status">Carregando chamados...</p>
  if (erro) return <p className={styles.erro} role="alert">{erro}</p>

  return (
    <div>
      {/* Cabeçalho com título, contexto da Empresa (tenant) e contador total */}
      <div className={styles.cabecalho}>
        <div>
          <h1 className={styles.titulo}>Chamados</h1>
          {empresaNome && <p className={styles.subtitulo}>{empresaNome}</p>}
        </div>
        <span className={styles.total}>{chamados.length} total</span>
      </div>

      {chamados.length === 0 ? (
        <p className={styles.info}>Nenhum chamado encontrado.</p>
      ) : (
        <div className={styles.lista}>
          {chamados.map(c => (
            <div key={c.ID} className={styles.card}>
              {/* Topo do card: categoria e fila */}
              <div className={styles.cardTopo}>
                <span className={styles.categoria}>{c.Categoria}</span>
                <span className={styles.fila}>{c.Fila}</span>
              </div>

              {/* Resumo/descrição do chamado */}
              <p className={styles.resumo}>{c.Resumo ?? '—'}</p>

              {/* Rodapé do card: status (pílula colorida), prioridade (indicador + label) e data */}
              <div className={styles.cardRodape}>
                <span className={`${styles.status} ${styles[`status--${STATUS_COR[c.Status]}`]}`}>
                  {STATUS_LABEL[c.Status]}
                </span>
                <span className={styles.prioridade}>
                  <span
                    className={styles.prioridadePonto}
                    style={{ background: PRIORIDADE_COR[c.Prioridade] }}
                  />
                  {c.Prioridade}
                </span>
                <span className={styles.data}>
                  {new Date(c.Criacao).toLocaleDateString('pt-BR')}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
