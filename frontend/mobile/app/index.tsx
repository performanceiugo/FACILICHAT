// Tela inicial do app — verifica autenticação e redireciona para a rota correta
// Exibe um spinner enquanto aguarda a leitura do token no SecureStore

import { useEffect } from 'react'
import { useRouter } from 'expo-router'
import { View, ActivityIndicator } from 'react-native'
import { auth } from '@/lib/auth'
import { theme } from '@/lib/theme'

export default function Index() {
  const router = useRouter()

  useEffect(() => {
    // Verifica token de forma assíncrona — SecureStore é async, diferente do localStorage
    auth.autenticado().then(ok => {
      router.replace(ok ? '/(tabs)/chamados' : '/(auth)/login')
    })
  }, [router])

  // Spinner azul centralizado enquanto a verificação ocorre
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <ActivityIndicator size="large" color={theme.colors.brandBlue} />
    </View>
  )
}
