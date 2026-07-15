'use client'

// Página de manutenção do catálogo de categorias do Gestor (Fase 4).
// Autoatendimento: listar, criar, renomear e ativar/desativar — nunca excluir (anti-amnésia),
// já que chamados antigos continuam apontando para a categoria mesmo desativada.

import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '@/lib/api'
import type { CategoriaChamado } from '@/types'
import styles from './categorias.module.css'

export default function CategoriasPage() {
  const [categorias, setCategorias] = useState<CategoriaChamado[]>([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState('')
  const montadoRef = useRef(true)

  const [nomeNovo, setNomeNovo] = useState('')
  const [criando, setCriando] = useState(false)
  const [erroCriar, setErroCriar] = useState('')

  // Edição de nome é por linha: só uma categoria por vez entra em modo de edição.
  const [editandoID, setEditandoID] = useState<string | null>(null)
  const [nomeEditado, setNomeEditado] = useState('')
  const [salvandoID, setSalvandoID] = useState<string | null>(null)
  const [erroLinha, setErroLinha] = useState<Record<string, string>>({})

  const buscarCategorias = useCallback(() => {
    setCarregando(true)
    api.categorias.listar()
      .then(lista => {
        if (!montadoRef.current) return
        setCategorias([...lista].sort((a, b) => a.Nome.localeCompare(b.Nome, 'pt-BR')))
        setErro('')
      })
      .catch((err: unknown) => {
        if (montadoRef.current) setErro(err instanceof Error ? err.message : 'Não foi possível carregar as categorias.')
      })
      .finally(() => {
        if (montadoRef.current) setCarregando(false)
      })
  }, [])

  useEffect(() => {
    montadoRef.current = true
    buscarCategorias()
    return () => { montadoRef.current = false }
  }, [buscarCategorias])

  async function criarCategoria(evento: React.FormEvent) {
    evento.preventDefault()
    const nome = nomeNovo.trim()
    if (!nome) return

    setCriando(true)
    setErroCriar('')
    try {
      const categoria = await api.categorias.criar({ Nome: nome })
      setCategorias(atual => [...atual, categoria].sort((a, b) => a.Nome.localeCompare(b.Nome, 'pt-BR')))
      setNomeNovo('')
    } catch (err) {
      setErroCriar(err instanceof Error ? err.message : 'Não foi possível criar a categoria.')
    } finally {
      setCriando(false)
    }
  }

  function iniciarEdicao(categoria: CategoriaChamado) {
    setEditandoID(categoria.ID)
    setNomeEditado(categoria.Nome)
    setErroLinha(atual => ({ ...atual, [categoria.ID]: '' }))
  }

  function cancelarEdicao() {
    setEditandoID(null)
    setNomeEditado('')
  }

  async function salvarNome(categoriaID: string) {
    const nome = nomeEditado.trim()
    if (!nome) return

    setSalvandoID(categoriaID)
    setErroLinha(atual => ({ ...atual, [categoriaID]: '' }))
    try {
      const categoria = await api.categorias.atualizar(categoriaID, { Nome: nome })
      setCategorias(atual =>
        [...atual.map(c => (c.ID === categoriaID ? categoria : c))].sort((a, b) => a.Nome.localeCompare(b.Nome, 'pt-BR')),
      )
      setEditandoID(null)
    } catch (err) {
      setErroLinha(atual => ({
        ...atual,
        [categoriaID]: err instanceof Error ? err.message : 'Não foi possível salvar o nome.',
      }))
    } finally {
      setSalvandoID(null)
    }
  }

  async function alternarAtiva(categoria: CategoriaChamado) {
    setSalvandoID(categoria.ID)
    setErroLinha(atual => ({ ...atual, [categoria.ID]: '' }))
    try {
      const atualizada = await api.categorias.atualizar(categoria.ID, { Ativa: !categoria.Ativa })
      setCategorias(atual => atual.map(c => (c.ID === categoria.ID ? atualizada : c)))
    } catch (err) {
      setErroLinha(atual => ({
        ...atual,
        [categoria.ID]: err instanceof Error ? err.message : 'Não foi possível alterar o status.',
      }))
    } finally {
      setSalvandoID(null)
    }
  }

  return (
    <div className={styles.pagina}>
      <header className={styles.cabecalho}>
        <div>
          <span className={styles.sobretitulo}>PAINEL DO GESTOR</span>
          <h1 className={styles.titulo}>Categorias</h1>
          <p className={styles.subtitulo}>
            Catálogo de categorias usado na abertura de chamados. Desativar não apaga nem afeta chamados já criados.
          </p>
        </div>
      </header>

      {/* Criação fica sempre visível no topo — fluxo mais comum desta tela. */}
      <form className={styles.formCriar} onSubmit={criarCategoria}>
        <label className={styles.campo}>
          <span>Nova categoria</span>
          <input
            type="text"
            value={nomeNovo}
            onChange={evento => setNomeNovo(evento.target.value)}
            placeholder="Ex.: Elevador, Portaria, Jardinagem"
            maxLength={80}
          />
        </label>
        <button type="submit" className={styles.botaoPrimario} disabled={criando || !nomeNovo.trim()}>
          {criando ? 'Adicionando...' : 'Adicionar'}
        </button>
        {erroCriar && <span className={styles.erroInline} role="alert">{erroCriar}</span>}
      </form>

      {carregando && <p className={styles.info} role="status">Carregando categorias...</p>}
      {!carregando && erro && <p className={styles.erro} role="alert">{erro}</p>}

      {!carregando && !erro && categorias.length === 0 && (
        <div className={styles.vazio}>
          <strong>Nenhuma categoria cadastrada</strong>
          <span>Adicione a primeira categoria acima para liberar a abertura de chamados.</span>
        </div>
      )}

      {!carregando && !erro && categorias.length > 0 && (
        <section className={styles.tabelaPainel} aria-label="Lista de categorias">
          <div className={styles.tabelaContainer}>
            <table className={styles.tabela}>
              <thead>
                <tr><th>Nome</th><th>Status</th><th aria-label="Ações" /></tr>
              </thead>
              <tbody>
                {categorias.map(categoria => {
                  const emEdicao = editandoID === categoria.ID
                  const salvando = salvandoID === categoria.ID
                  return (
                    <tr key={categoria.ID}>
                      <td>
                        {emEdicao ? (
                          <input
                            type="text"
                            className={styles.inputLinha}
                            value={nomeEditado}
                            onChange={evento => setNomeEditado(evento.target.value)}
                            maxLength={80}
                            autoFocus
                          />
                        ) : (
                          <strong>{categoria.Nome}</strong>
                        )}
                        {erroLinha[categoria.ID] && (
                          <small className={styles.erroLinha}>{erroLinha[categoria.ID]}</small>
                        )}
                      </td>
                      <td>
                        <span className={`${styles.status} ${categoria.Ativa ? styles['status--sucesso'] : styles['status--apagado']}`}>
                          {categoria.Ativa ? 'Ativa' : 'Inativa'}
                        </span>
                      </td>
                      <td className={styles.acoes}>
                        {emEdicao ? (
                          <>
                            <button type="button" className={styles.link} onClick={() => salvarNome(categoria.ID)} disabled={salvando || !nomeEditado.trim()}>
                              {salvando ? 'Salvando...' : 'Salvar'}
                            </button>
                            <button type="button" className={styles.link} onClick={cancelarEdicao} disabled={salvando}>Cancelar</button>
                          </>
                        ) : (
                          <>
                            <button type="button" className={styles.link} onClick={() => iniciarEdicao(categoria)} disabled={salvando}>Editar</button>
                            <button type="button" className={styles.link} onClick={() => alternarAtiva(categoria)} disabled={salvando}>
                              {salvando ? '...' : categoria.Ativa ? 'Desativar' : 'Ativar'}
                            </button>
                          </>
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  )
}
