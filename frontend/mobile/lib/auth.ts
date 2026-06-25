import * as SecureStore from 'expo-secure-store'
import type { TokenResposta, UsuarioFuncao } from './types'

export const auth = {
  async salvar(dados: TokenResposta) {
    await SecureStore.setItemAsync('token', dados.token_acesso)
    await SecureStore.setItemAsync('funcao', dados.funcao)
    await SecureStore.setItemAsync('nome', dados.nome)
  },

  token: () => SecureStore.getItemAsync('token'),
  funcao: () => SecureStore.getItemAsync('funcao') as Promise<UsuarioFuncao | null>,
  nome: () => SecureStore.getItemAsync('nome'),

  async autenticado(): Promise<boolean> {
    const t = await SecureStore.getItemAsync('token')
    return !!t
  },

  async sair() {
    await SecureStore.deleteItemAsync('token')
    await SecureStore.deleteItemAsync('funcao')
    await SecureStore.deleteItemAsync('nome')
  },

  async isGerente(): Promise<boolean> {
    return (await SecureStore.getItemAsync('funcao')) === 'Gerente'
  },

  async isSupervisor(): Promise<boolean> {
    const f = await SecureStore.getItemAsync('funcao')
    return f === 'Supervisor' || f === 'Gerente'
  },
}
