'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import type { Chamado } from '@/types'
import styles from './chamados.module.css'

const STATUS_LABEL: Record<string, string> = {
  Recebido: 'Recebido',
  EmAndamento: 'Em Andamento',
  Agendado: 'Agendado',
  Concluido: 'Concluído',
  Cancelado: 'Cancelado',
}

const PRIORIDADE_COR: Record<string, string> = {
  Baixa: '#16a34a',
  Media: '#d97706',
  Alta: '#dc2626',
  Critica: '#7c3aed',
}

export default function ChamadosPage() {
  const [chamados, setChamados] = useState<Chamado[]>([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState('')

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
              <div className={styles.cardTopo}>
                <span className={styles.categoria}>{c.Categoria}</span>
                <span className={styles.fila}>{c.Fila}</span>
              </div>
              <p className={styles.resumo}>{c.Resumo ?? '—'}</p>
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
