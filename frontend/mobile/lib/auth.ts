// Gerenciamento de sessão no app mobile
// Usa expo-secure-store (armazenamento criptografado) em vez de localStorage
// Todas as operações são assíncronas — use await ao chamar os métodos

import * as SecureStore from 'expo-secure-store'
import type { TokenResposta, UsuarioFuncao } from './types'

export const auth = {
  // Salva os dados de sessão após login bem-sucedido
  async salvar(dados: TokenResposta) {
    await SecureStore.setItemAsync('token', dados.token_acesso)
    await SecureStore.setItemAsync('funcao', dados.funcao)
    await SecureStore.setItemAsync('nome', dados.nome)
  },

  token: () => SecureStore.getItemAsync('token'),
  funcao: () => SecureStore.getItemAsync('funcao') as Promise<UsuarioFuncao | null>,
  nome: () => SecureStore.getItemAsync('nome'),

  // Verifica se há sessão ativa (token salvo no SecureStore)
  async autenticado(): Promise<boolean> {
    const t = await SecureStore.getItemAsync('token')
    return !!t
  },

  // Remove todos os dados de sessão — chamado no logout
  async sair() {
    await SecureStore.deleteItemAsync('token')
    await SecureStore.deleteItemAsync('funcao')
    await SecureStore.deleteItemAsync('nome')
  },

  async isGestor(): Promise<boolean> {
    return (await SecureStore.getItemAsync('funcao')) === 'Gestor'
  },

  // Supervisores e gestores têm acesso às funcionalidades de supervisão
  async isSupervisor(): Promise<boolean> {
    const f = await SecureStore.getItemAsync('funcao')
    return f === 'Supervisor' || f === 'Gestor'
  },
}
