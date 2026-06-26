// Tela de login do app mobile
// Após autenticação bem-sucedida, redireciona para a aba de chamados

import { useState } from 'react'
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native'
import { useRouter } from 'expo-router'
import { api } from '@/lib/api'
import { auth } from '@/lib/auth'

export default function LoginScreen() {
  const router = useRouter()

  // Estado dos campos e controle de carregamento/erro
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState('')
  const [carregando, setCarregando] = useState(false)

  async function handleLogin() {
    setErro('')
    setCarregando(true)
    try {
      // Autentica com o backend e salva os dados no SecureStore
      const dados = await api.login(email, senha)
      await auth.salvar(dados)
      router.replace('/(tabs)/chamados')
    } catch (err) {
      setErro(err instanceof Error ? err.message : 'Erro ao fazer login')
    } finally {
      setCarregando(false)
    }
  }

  return (
    <View style={s.container}>
      <Text style={s.titulo}>FaciliChat</Text>
      <Text style={s.subtitulo}>Acesse sua conta</Text>

      {/* Campo de email com teclado específico e sem capitalização automática */}
      <TextInput
        style={s.input}
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
        autoComplete="email"
      />

      {/* Campo de senha com entrada oculta */}
      <TextInput
        style={s.input}
        placeholder="Senha"
        value={senha}
        onChangeText={setSenha}
        secureTextEntry
        autoComplete="current-password"
      />

      {/* Exibe mensagem de erro apenas quando há falha */}
      {!!erro && <Text style={s.erro}>{erro}</Text>}

      {/* Botão desabilitado durante o carregamento para evitar múltiplas requisições */}
      <TouchableOpacity style={s.botao} onPress={handleLogin} disabled={carregando}>
        {carregando
          ? <ActivityIndicator color="#fff" />
          : <Text style={s.botaoTexto}>Entrar</Text>
        }
      </TouchableOpacity>
    </View>
  )
}

// Estilos da tela de login
const s = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 24,
    backgroundColor: '#f9fafb',
  },
  titulo: {
    fontSize: 28,
    fontWeight: '700',
    color: '#1a56db',
    textAlign: 'center',
    marginBottom: 4,
  },
  subtitulo: {
    fontSize: 15,
    color: '#6b7280',
    textAlign: 'center',
    marginBottom: 32,
  },
  input: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#e5e7eb',
    borderRadius: 10,
    padding: 14,
    fontSize: 16,
    marginBottom: 12,
  },
  erro: {
    color: '#dc2626',
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 8,
  },
  botao: {
    backgroundColor: '#1a56db',
    borderRadius: 10,
    padding: 16,
    alignItems: 'center',
    marginTop: 4,
  },
  botaoTexto: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 16,
  },
})
