'use client'

// Página de manutenção da equipe do Gestor (Fase 4).
// Autoatendimento: listar, contratar (reaproveita POST /usuarios/equipe), editar dados cadastrais
// e ativar/desativar — "remover" alguém é sempre desativação, nunca exclusão (anti-amnésia),
// preservando o histórico dos chamados que essa pessoa já atendeu. Tela separada do dashboard de
// métricas em /painel/supervisores (que continua só leitura).

import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '@/lib/api'
import { auth } from '@/lib/auth'
import { aoInvalidarCampo, limparValidacaoCustomizada } from '@/lib/validacao'
import type { Usuario, UsuarioFuncao } from '@/types'
import styles from './equipe.module.css'

// Papéis geridos nesta tela — Cliente não é "equipe" (é o contrato/condomínio atendido) e
// Superadmin nasce só pelo bootstrap da plataforma, fora do escopo do Gestor de uma Empresa.
const FUNCOES_EQUIPE: UsuarioFuncao[] = ['Supervisor', 'Funcionario', 'RH', 'Financeiro', 'Gestor']

const FUNCAO_LABEL: Record<UsuarioFuncao, string> = {
  Cliente: 'Cliente',
  Supervisor: 'Supervisor',
  Funcionario: 'Funcionário',
  RH: 'RH',
  Financeiro: 'Financeiro',
  Gestor: 'Gestor',
  Superadmin: 'Superadmin',
}

const FORM_INICIAL = { Nome: '', Email: '', Senha: '', Telefone: '', Funcao: 'Supervisor' as UsuarioFuncao }

export default function EquipePage() {
  const [equipe, setEquipe] = useState<Usuario[]>([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState('')
  const montadoRef = useRef(true)

  const [form, setForm] = useState(FORM_INICIAL)
  const [criando, setCriando] = useState(false)
  const [erroCriar, setErroCriar] = useState('')

  // Edição de dados cadastrais é por linha: Nome/Email/Telefone viram inputs só na linha ativa.
  const [editandoID, setEditandoID] = useState<string | null>(null)
  const [formEdicao, setFormEdicao] = useState({ Nome: '', Email: '', Telefone: '' })
  const [salvandoID, setSalvandoID] = useState<string | null>(null)
  const [erroLinha, setErroLinha] = useState<Record<string, string>>({})

  const buscarEquipe = useCallback(() => {
    setCarregando(true)
    api.usuarios.equipe()
      .then(lista => {
        if (!montadoRef.current) return
        // Cliente não aparece aqui: esta tela é só sobre a equipe interna da Empresa.
        setEquipe(lista.filter(u => u.Funcao !== 'Cliente').sort((a, b) => a.Nome.localeCompare(b.Nome, 'pt-BR')))
        setErro('')
      })
      .catch((err: unknown) => {
        if (montadoRef.current) setErro(err instanceof Error ? err.message : 'Não foi possível carregar a equipe.')
      })
      .finally(() => {
        if (montadoRef.current) setCarregando(false)
      })
  }, [])

  useEffect(() => {
    montadoRef.current = true
    buscarEquipe()
    return () => { montadoRef.current = false }
  }, [buscarEquipe])

  async function contratar(evento: React.FormEvent) {
    evento.preventDefault()
    setCriando(true)
    setErroCriar('')
    try {
      const empresaID = auth.empresaId()
      if (!empresaID) throw new Error('Sessão sem Empresa identificada — faça login novamente.')

      const usuario = await api.usuarios.criarEquipe({
        EmpresaID: empresaID,
        Nome: form.Nome,
        Email: form.Email,
        Senha: form.Senha,
        Funcao: form.Funcao,
        Telefone: form.Telefone || undefined,
      })
      setEquipe(atual => [...atual, usuario].sort((a, b) => a.Nome.localeCompare(b.Nome, 'pt-BR')))
      setForm(FORM_INICIAL)
    } catch (err) {
      setErroCriar(err instanceof Error ? err.message : 'Não foi possível adicionar este membro da equipe.')
    } finally {
      setCriando(false)
    }
  }

  function iniciarEdicao(usuario: Usuario) {
    setEditandoID(usuario.ID)
    setFormEdicao({ Nome: usuario.Nome, Email: usuario.Email, Telefone: usuario.Telefone ?? '' })
    setErroLinha(atual => ({ ...atual, [usuario.ID]: '' }))
  }

  function cancelarEdicao() {
    setEditandoID(null)
  }

  async function salvarEdicao(usuarioID: string) {
    setSalvandoID(usuarioID)
    setErroLinha(atual => ({ ...atual, [usuarioID]: '' }))
    try {
      const usuario = await api.usuarios.editar(usuarioID, {
        Nome: formEdicao.Nome,
        Email: formEdicao.Email,
        Telefone: formEdicao.Telefone || undefined,
      })
      setEquipe(atual =>
        [...atual.map(u => (u.ID === usuarioID ? usuario : u))].sort((a, b) => a.Nome.localeCompare(b.Nome, 'pt-BR')),
      )
      setEditandoID(null)
    } catch (err) {
      setErroLinha(atual => ({
        ...atual,
        [usuarioID]: err instanceof Error ? err.message : 'Não foi possível salvar os dados.',
      }))
    } finally {
      setSalvandoID(null)
    }
  }

  async function alternarAtivo(usuario: Usuario) {
    setSalvandoID(usuario.ID)
    setErroLinha(atual => ({ ...atual, [usuario.ID]: '' }))
    try {
      const atualizado = await api.usuarios.alterarStatus(usuario.ID, !usuario.Ativo)
      setEquipe(atual => atual.map(u => (u.ID === usuario.ID ? atualizado : u)))
    } catch (err) {
      setErroLinha(atual => ({
        ...atual,
        [usuario.ID]: err instanceof Error ? err.message : 'Não foi possível alterar o status.',
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
          <h1 className={styles.titulo}>Equipe</h1>
          <p className={styles.subtitulo}>
            Contrate, edite dados cadastrais e ative ou desative a equipe interna. Desativar preserva o histórico de chamados já atendidos.
          </p>
        </div>
      </header>

      {/* Contratação fica sempre visível no topo — fluxo mais comum desta tela. */}
      <form className={styles.formCriar} onSubmit={contratar}>
        <label className={styles.campo}>
          <span>Nome</span>
          <input
            type="text"
            value={form.Nome}
            onChange={e => setForm({ ...form, Nome: e.target.value })}
            maxLength={120}
            required
            onInvalid={aoInvalidarCampo}
            onInput={limparValidacaoCustomizada}
          />
        </label>
        <label className={styles.campo}>
          <span>Email</span>
          <input
            type="email"
            value={form.Email}
            onChange={e => setForm({ ...form, Email: e.target.value })}
            maxLength={120}
            required
            onInvalid={aoInvalidarCampo}
            onInput={limparValidacaoCustomizada}
          />
        </label>
        <label className={styles.campo}>
          <span>Senha inicial</span>
          <input
            type="password"
            value={form.Senha}
            onChange={e => setForm({ ...form, Senha: e.target.value })}
            minLength={15}
            maxLength={128}
            required
            onInvalid={aoInvalidarCampo}
            onInput={limparValidacaoCustomizada}
          />
        </label>
        <label className={styles.campo}>
          <span>Função</span>
          <select value={form.Funcao} onChange={e => setForm({ ...form, Funcao: e.target.value as UsuarioFuncao })}>
            {FUNCOES_EQUIPE.map(f => <option key={f} value={f}>{FUNCAO_LABEL[f]}</option>)}
          </select>
        </label>
        <label className={styles.campo}>
          <span>Telefone (opcional)</span>
          <input
            type="text"
            value={form.Telefone}
            onChange={e => setForm({ ...form, Telefone: e.target.value })}
            maxLength={20}
          />
        </label>
        <button type="submit" className={styles.botaoPrimario} disabled={criando}>
          {criando ? 'Adicionando...' : 'Adicionar à equipe'}
        </button>
        {erroCriar && <span className={styles.erroInline} role="alert">{erroCriar}</span>}
      </form>

      {carregando && <p className={styles.info} role="status">Carregando equipe...</p>}
      {!carregando && erro && <p className={styles.erro} role="alert">{erro}</p>}

      {!carregando && !erro && equipe.length === 0 && (
        <div className={styles.vazio}>
          <strong>Nenhum membro da equipe cadastrado</strong>
          <span>Adicione o primeiro acima para começar a atribuir chamados.</span>
        </div>
      )}

      {!carregando && !erro && equipe.length > 0 && (
        <section className={styles.tabelaPainel} aria-label="Lista da equipe">
          <div className={styles.tabelaContainer}>
            <table className={styles.tabela}>
              <thead>
                <tr><th>Nome</th><th>Email</th><th>Função</th><th>Telefone</th><th>Status</th><th aria-label="Ações" /></tr>
              </thead>
              <tbody>
                {equipe.map(usuario => {
                  const emEdicao = editandoID === usuario.ID
                  const salvando = salvandoID === usuario.ID
                  return (
                    <tr key={usuario.ID}>
                      <td>
                        {emEdicao ? (
                          <input
                            type="text"
                            className={styles.inputLinha}
                            value={formEdicao.Nome}
                            onChange={e => setFormEdicao({ ...formEdicao, Nome: e.target.value })}
                            maxLength={120}
                            autoFocus
                          />
                        ) : (
                          <strong>{usuario.Nome}</strong>
                        )}
                      </td>
                      <td>
                        {emEdicao ? (
                          <input
                            type="email"
                            className={styles.inputLinha}
                            value={formEdicao.Email}
                            onChange={e => setFormEdicao({ ...formEdicao, Email: e.target.value })}
                            maxLength={120}
                          />
                        ) : usuario.Email}
                      </td>
                      <td>{FUNCAO_LABEL[usuario.Funcao]}</td>
                      <td>
                        {emEdicao ? (
                          <input
                            type="text"
                            className={styles.inputLinha}
                            value={formEdicao.Telefone}
                            onChange={e => setFormEdicao({ ...formEdicao, Telefone: e.target.value })}
                            maxLength={20}
                          />
                        ) : (usuario.Telefone || '—')}
                      </td>
                      <td>
                        <span className={`${styles.status} ${usuario.Ativo ? styles['status--sucesso'] : styles['status--apagado']}`}>
                          {usuario.Ativo ? 'Ativo' : 'Inativo'}
                        </span>
                        {erroLinha[usuario.ID] && <small className={styles.erroLinha}>{erroLinha[usuario.ID]}</small>}
                      </td>
                      <td className={styles.acoes}>
                        {emEdicao ? (
                          <>
                            <button type="button" className={styles.link} onClick={() => salvarEdicao(usuario.ID)} disabled={salvando}>
                              {salvando ? 'Salvando...' : 'Salvar'}
                            </button>
                            <button type="button" className={styles.link} onClick={cancelarEdicao} disabled={salvando}>Cancelar</button>
                          </>
                        ) : (
                          <>
                            <button type="button" className={styles.link} onClick={() => iniciarEdicao(usuario)} disabled={salvando}>Editar</button>
                            <button type="button" className={styles.link} onClick={() => alternarAtivo(usuario)} disabled={salvando}>
                              {salvando ? '...' : usuario.Ativo ? 'Desativar' : 'Ativar'}
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
