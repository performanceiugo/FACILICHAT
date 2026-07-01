'use client'

// Página de listagem de chamados do painel web
// Gestores e supervisores veem todos os chamados; clientes veem apenas os seus (filtro no backend)

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import type { Chamado } from '@/types'
import styles from './chamados.module.css'

// Labels amigáveis para exibição dos status no card
const STATUS_LABEL: Record<string, string> = {
  Recebido: 'Recebido',
  EmAndamento: 'Em Andamento',
  Agendado: 'Agendado',
  Concluido: 'Concluído',
  Cancelado: 'Cancelado',
}

// Cores de destaque para cada nível de prioridade
const PRIORIDADE_COR: Record<string, string> = {
  Baixa: '#16a34a',   // verde
  Media: '#d97706',   // amarelo
  Alta: '#dc2626',    // vermelho
  Critica: '#7c3aed', // roxo
}

export default function ChamadosPage() {
  const [chamados, setChamados] = useState<Chamado[]>([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState('')

  // Busca os chamados ao montar o componente
  useEffect(() => {
    api.chamados.listar()
      .then(setChamados)
      .catch(err => setErro(err.message))
      .finally(() => setCarregando(false))
  }, [])

  if (carregando) return <p className={styles.info}>Carregando chamados...</p>
  if (erro) return <p className={styles.erro}>{erro}</p>

  return (
    <div>
      {/* Cabeçalho com título e contador total */}
      <div className={styles.cabecalho}>
        <h1 className={styles.titulo}>Chamados</h1>
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

              {/* Rodapé do card: status, prioridade colorida e data */}
              <div className={styles.cardRodape}>
                <span className={styles.status}>{STATUS_LABEL[c.Status]}</span>
                <span
                  className={styles.prioridade}
                  style={{ color: PRIORIDADE_COR[c.Prioridade] }}
                >
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
