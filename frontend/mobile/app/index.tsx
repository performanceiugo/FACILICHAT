import { useEffect } from 'react'
import { useRouter } from 'expo-router'
import { View, ActivityIndicator } from 'react-native'
import { auth } from '@/lib/auth'

export default function Index() {
  const router = useRouter()

  useEffect(() => {
    auth.autenticado().then(ok => {
      router.replace(ok ? '/(tabs)/chamados' : '/(auth)/login')
    })
  }, [router])

  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <ActivityIndicator size="large" color="#1a56db" />
    </View>
  )
}
