'use client'

import { useEffect, useRef, useState } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import { auth } from '@/lib/auth'
// Mensagens de validação nativa do navegador em português (item M13)
import { aoInvalidarCampo, limparValidacaoCustomizada } from '@/lib/validacao'
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
  // Item B2: guarda de montagem — evita setState após a tela ser desmontada (ex.: navegação
  // para fora antes de `carregarEmpresas` responder).
  const montadoRef = useRef(true)

  async function carregarEmpresas() {
    const dados = await api.plataforma.listarEmpresas()
    if (montadoRef.current) setEmpresas(dados)
  }

  useEffect(() => {
    montadoRef.current = true
    if (!auth.autenticado()) {
      router.push('/login')
      return
    }
    if (!auth.isSuperadmin()) {
      router.push('/painel/visao-geral')
      return
    }
    // `queueMicrotask` evita chamar o setter direto no corpo síncrono do efeito — o Next.js 16/
    // React Compiler ESLint (`react-hooks/set-state-in-effect`) não permite.
    queueMicrotask(() => setNome(auth.nome()))
    carregarEmpresas()
      .catch(err => {
        if (montadoRef.current) setErro(err instanceof Error ? err.message : 'Erro ao carregar empresas')
      })
      .finally(() => {
        if (montadoRef.current) setCarregado(true)
      })
    return () => { montadoRef.current = false }
  }, [router])

  // Logout via backend: só ele apaga o cookie `HttpOnly` da sessão (item S6).
  async function sair() {
    await api.logout()
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
                onInvalid={aoInvalidarCampo}
                onInput={limparValidacaoCustomizada}
              />
            </div>
            <div className={styles.grupo}>
              <label htmlFor="cnpj">CNPJ</label>
              <input
                id="cnpj"
                value={form.cnpj}
                onChange={e => setForm({ ...form, cnpj: e.target.value })}
                required
                onInvalid={aoInvalidarCampo}
                onInput={limparValidacaoCustomizada}
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
                    onInvalid={aoInvalidarCampo}
                    onInput={limparValidacaoCustomizada}
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
                    onInvalid={aoInvalidarCampo}
                    onInput={limparValidacaoCustomizada}
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
                    onInvalid={aoInvalidarCampo}
                    onInput={limparValidacaoCustomizada}
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

            {/* role="alert" anuncia a falha imediatamente em leitores de tela (item B5) */}
            {erro && <p className={styles.erro} role="alert">{erro}</p>}
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
