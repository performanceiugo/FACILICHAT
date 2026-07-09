// Tela de perfil do usuário no app mobile
// Exibe dados do usuário autenticado e oferece opção de logout

import { useEffect, useState } from 'react'
import { View, Text, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native'
import { useRouter } from 'expo-router'
import { api } from '@/lib/api'
import { auth } from '@/lib/auth'
import type { Usuario } from '@/lib/types'
import { theme } from '@/lib/theme'

export default function PerfilScreen() {
  const router = useRouter()
  const [usuario, setUsuario] = useState<Usuario | null>(null)
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState('')

  // Busca os dados do usuário autenticado ao abrir a tela
  async function carregarPerfil() {
    try {
      setErro('')
      const dados = await api.eu()
      setUsuario(dados)
    } catch (err) {
      setErro(err instanceof Error ? err.message : 'Erro ao carregar perfil')
    } finally {
      setCarregando(false)
    }
  }

  useEffect(() => {
    carregarPerfil()
  }, [])

  // Remove sessão do SecureStore e retorna para a tela de login
  async function sair() {
    await auth.sair()
    router.replace('/(auth)/login')
  }

  if (carregando) {
    return (
      <View style={s.centro}>
        <ActivityIndicator size="large" color={theme.colors.brandBlue} />
      </View>
    )
  }

  if (erro) {
    return (
      <View style={s.centro}>
        <Text style={s.erro}>{erro}</Text>
        <TouchableOpacity style={s.botaoRetry} onPress={carregarPerfil}>
          <Text style={s.botaoRetryTexto}>Tentar novamente</Text>
        </TouchableOpacity>
      </View>
    )
  }

  return (
    <View style={s.container}>
      {/* Card com informações do usuário */}
      <View style={s.card}>
        <Text style={s.nome}>{usuario?.Nome}</Text>
        <Text style={s.email}>{usuario?.Email}</Text>
        {/* Badge com a função/perfil do usuário */}
        <View style={s.tag}><Text style={s.tagTexto}>{usuario?.Funcao}</Text></View>
        {/* Condomínio exibido apenas quando preenchido */}
        {usuario?.Condominio && (
          <Text style={s.condominio}>{usuario.Condominio}</Text>
        )}
      </View>

      {/* Botão de logout com texto vermelho */}
      <TouchableOpacity style={s.botaoSair} onPress={sair}>
        <Text style={s.botaoSairTexto}>Sair</Text>
      </TouchableOpacity>
    </View>
  )
}

// Estilos da tela de perfil
const s = StyleSheet.create({
  centro: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  container: { flex: 1, padding: 24, backgroundColor: theme.colors.surfacePage },
  card: {
    backgroundColor: theme.colors.surfaceCard,
    borderRadius: theme.radius.card,
    padding: 24,
    borderWidth: 1,
    borderColor: theme.colors.borderSoft,
    gap: 8,
    alignItems: 'center',
    marginBottom: 24,
  },
  erro: { color: theme.colors.danger, fontFamily: theme.typography.fontFamily, marginBottom: theme.spacing.md },
  botaoRetry: {
    backgroundColor: theme.colors.brandBlue,
    borderRadius: theme.radius.control,
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.md,
  },
  botaoRetryTexto: { color: theme.colors.white, fontFamily: theme.typography.fontFamilySemiBold },
  nome: { fontSize: 20, fontFamily: theme.typography.fontFamilyBold, color: theme.colors.ink900 },
  email: { fontSize: 14, color: theme.colors.ink500, fontFamily: theme.typography.fontFamily },
  tag: {
    backgroundColor: theme.colors.brandBlueSoft,
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: theme.radius.pill,
    marginTop: 4,
  },
  tagTexto: { color: theme.colors.brandBlue, fontFamily: theme.typography.fontFamilySemiBold, fontSize: 13 },
  condominio: { fontSize: 14, color: theme.colors.ink500, marginTop: 4, fontFamily: theme.typography.fontFamily },
  botaoSair: {
    borderWidth: 1,
    borderColor: theme.colors.borderSoft,
    borderRadius: theme.radius.control,
    padding: 16,
    alignItems: 'center',
    backgroundColor: theme.colors.surfaceCard,
  },
  botaoSairTexto: { color: theme.colors.danger, fontFamily: theme.typography.fontFamilySemiBold, fontSize: 15 },
})
