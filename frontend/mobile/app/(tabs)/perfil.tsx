// Tela de perfil do usuário no app mobile
// Exibe dados do usuário autenticado e oferece opção de logout

import { useEffect, useState } from 'react'
import { View, Text, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native'
import { useRouter } from 'expo-router'
import { api } from '@/lib/api'
import { auth } from '@/lib/auth'
import type { Usuario } from '@/lib/types'

export default function PerfilScreen() {
  const router = useRouter()
  const [usuario, setUsuario] = useState<Usuario | null>(null)
  const [carregando, setCarregando] = useState(true)

  // Busca os dados do usuário autenticado ao abrir a tela
  useEffect(() => {
    api.eu()
      .then(setUsuario)
      .finally(() => setCarregando(false))
  }, [])

  // Remove sessão do SecureStore e retorna para a tela de login
  async function sair() {
    await auth.sair()
    router.replace('/(auth)/login')
  }

  if (carregando) {
    return (
      <View style={s.centro}>
        <ActivityIndicator size="large" color="#1a56db" />
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
  container: { flex: 1, padding: 24, backgroundColor: '#f9fafb' },
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 24,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    gap: 8,
    alignItems: 'center',
    marginBottom: 24,
  },
  nome: { fontSize: 20, fontWeight: '700', color: '#111827' },
  email: { fontSize: 14, color: '#6b7280' },
  tag: {
    backgroundColor: '#eff6ff',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 999,
    marginTop: 4,
  },
  tagTexto: { color: '#1a56db', fontWeight: '600', fontSize: 13 },
  condominio: { fontSize: 14, color: '#6b7280', marginTop: 4 },
  botaoSair: {
    borderWidth: 1,
    borderColor: '#e5e7eb',
    borderRadius: 10,
    padding: 16,
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  botaoSairTexto: { color: '#dc2626', fontWeight: '600', fontSize: 15 },
})
