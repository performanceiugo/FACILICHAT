'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import { auth } from '@/lib/auth'
import type { Empresa } from '@/types'
import styles from './empresas.module.css'

const inicial = {
  nomeEmpresa: '',
  cnpj: '',
  nomeGestor: '',
  emailGestor: '',
  senhaGestor: '',
  telefoneGestor: '',
}

export default function EmpresasPlataformaPage() {
  const router = useRouter()
  const [carregado, setCarregado] = useState(false)
  const [nome, setNome] = useState<string | null>(null)
  const [empresas, setEmpresas] = useState<Empresa[]>([])
  const [form, setForm] = useState(inicial)
  const [erro, setErro] = useState('')
  const [carregando, setCarregando] = useState(false)

  async function carregarEmpresas() {
    const dados = await api.plataforma.listarEmpresas()
    setEmpresas(dados)
  }

  useEffect(() => {
    if (!auth.autenticado()) {
      router.push('/login')
      return
    }
    if (!auth.isSuperadmin()) {
      router.push('/painel/chamados')
      return
    }
    setNome(auth.nome())
    carregarEmpresas()
      .catch(err => setErro(err instanceof Error ? err.message : 'Erro ao carregar empresas'))
      .finally(() => setCarregado(true))
  }, [router])

  function sair() {
    auth.sair()
    router.push('/login')
  }

  async function criarEmpresa(e: React.FormEvent) {
    e.preventDefault()
    setErro('')
    setCarregando(true)
    try {
      await api.plataforma.criarEmpresa({
        Nome: form.nomeEmpresa,
        CNPJ: form.cnpj,
        Gestor: {
          Nome: form.nomeGestor,
          Email: form.emailGestor,
          Senha: form.senhaGestor,
          Telefone: form.telefoneGestor || undefined,
        },
      })
      setForm(inicial)
      await carregarEmpresas()
    } catch (err) {
      setErro(err instanceof Error ? err.message : 'Erro ao criar empresa')
    } finally {
      setCarregando(false)
    }
  }

  async function alternarStatus(empresa: Empresa) {
    setErro('')
    const novoStatus = empresa.Status === 'Ativa' ? 'Suspensa' : 'Ativa'
    try {
      const atualizada = await api.plataforma.atualizarStatusEmpresa(empresa.ID, novoStatus)
      setEmpresas(lista => lista.map(item => item.ID === atualizada.ID ? atualizada : item))
    } catch (err) {
      setErro(err instanceof Error ? err.message : 'Erro ao atualizar status')
    }
  }

  if (!carregado) return null

  return (
    <main className={styles.pagina}>
      <header className={styles.topo}>
        <div>
          <h1 className={styles.titulo}>Empresas</h1>
          <p className={styles.subtitulo}>Operacao da plataforma e onboarding de tenants</p>
        </div>
        <div className={styles.usuario}>
          <span className={styles.nome}>{nome}</span>
          <button type="button" onClick={sair} className={styles.botaoSecundario}>Sair</button>
        </div>
      </header>

      <div className={styles.grid}>
        <section className={styles.painel}>
          <h2 className={styles.painelTitulo}>Nova empresa</h2>
          <form onSubmit={criarEmpresa} className={styles.form}>
            <div className={styles.grupo}>
              <label htmlFor="nomeEmpresa">Empresa</label>
              <input
                id="nomeEmpresa"
                value={form.nomeEmpresa}
                onChange={e => setForm({ ...form, nomeEmpresa: e.target.value })}
                required
              />
            </div>
            <div className={styles.grupo}>
              <label htmlFor="cnpj">CNPJ</label>
              <input
                id="cnpj"
                value={form.cnpj}
                onChange={e => setForm({ ...form, cnpj: e.target.value })}
                required
              />
            </div>

            <div className={styles.divisor}>
              <h2 className={styles.painelTitulo}>Primeiro gestor</h2>
              <div className={styles.form}>
                <div className={styles.grupo}>
                  <label htmlFor="nomeGestor">Nome</label>
                  <input
                    id="nomeGestor"
                    value={form.nomeGestor}
                    onChange={e => setForm({ ...form, nomeGestor: e.target.value })}
                    required
                  />
                </div>
                <div className={styles.grupo}>
                  <label htmlFor="emailGestor">Email</label>
                  <input
                    id="emailGestor"
                    type="email"
                    value={form.emailGestor}
                    onChange={e => setForm({ ...form, emailGestor: e.target.value })}
                    required
                  />
                </div>
                <div className={styles.grupo}>
                  <label htmlFor="senhaGestor">Senha inicial</label>
                  <input
                    id="senhaGestor"
                    type="password"
                    value={form.senhaGestor}
                    onChange={e => setForm({ ...form, senhaGestor: e.target.value })}
                    required
                  />
                </div>
                <div className={styles.grupo}>
                  <label htmlFor="telefoneGestor">Telefone</label>
                  <input
                    id="telefoneGestor"
                    value={form.telefoneGestor}
                    onChange={e => setForm({ ...form, telefoneGestor: e.target.value })}
                  />
                </div>
              </div>
            </div>

            {erro && <p className={styles.erro}>{erro}</p>}
            <button type="submit" disabled={carregando} className={styles.botaoPrimario}>
              {carregando ? 'Criando...' : 'Criar empresa'}
            </button>
          </form>
        </section>

        <section className={styles.painel}>
          <h2 className={styles.painelTitulo}>Tenants cadastrados</h2>
          {empresas.length === 0 ? (
            <p className={styles.info}>Nenhuma empresa cadastrada.</p>
          ) : (
            <div className={styles.lista}>
              {empresas.map(empresa => (
                <article key={empresa.ID} className={styles.empresa}>
                  <div>
                    <div className={styles.empresaNome}>{empresa.Nome}</div>
                    <div className={styles.empresaMeta}>
                      {empresa.CNPJ} · criada em {new Date(empresa.Criacao).toLocaleDateString('pt-BR')}
                    </div>
                  </div>
                  <div className={styles.acoes}>
                    <span className={`${styles.status} ${empresa.Status === 'Ativa' ? styles.ativa : styles.suspensa}`}>
                      {empresa.Status}
                    </span>
                    <button
                      type="button"
                      onClick={() => alternarStatus(empresa)}
                      className={styles.botaoSecundario}
                    >
                      {empresa.Status === 'Ativa' ? 'Suspender' : 'Reativar'}
                    </button>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  )
}
