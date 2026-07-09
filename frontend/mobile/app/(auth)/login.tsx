// Tela de login do app mobile
// Após autenticação bem-sucedida, redireciona para a aba de chamados

import { useState } from 'react'
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native'
import { useRouter } from 'expo-router'
import { api } from '@/lib/api'
import { auth } from '@/lib/auth'
import { theme } from '@/lib/theme'

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
          ? <ActivityIndicator color={theme.colors.white} />
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
    padding: theme.spacing.xl,
    backgroundColor: theme.colors.surfacePage,
  },
  titulo: {
    fontSize: theme.fontSize.xl,
    fontFamily: theme.typography.fontFamilyBold,
    color: theme.colors.brandBlue,
    textAlign: 'center',
    marginBottom: theme.spacing.xs,
  },
  subtitulo: {
    fontSize: theme.fontSize.md,
    fontFamily: theme.typography.fontFamily,
    color: theme.colors.ink500,
    textAlign: 'center',
    marginBottom: theme.spacing.xxl,
  },
  input: {
    backgroundColor: theme.colors.surfaceCard,
    borderWidth: 1,
    borderColor: theme.colors.borderSoft,
    borderRadius: theme.radius.control,
    minHeight: theme.control.minHeight,
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.md,
    fontSize: theme.fontSize.base,
    fontFamily: theme.typography.fontFamily,
    color: theme.colors.ink900,
    marginBottom: theme.spacing.md,
  },
  erro: {
    color: theme.colors.danger,
    backgroundColor: theme.colors.dangerSoft,
    borderRadius: theme.radius.control,
    padding: theme.spacing.md,
    fontSize: theme.fontSize.sm,
    fontFamily: theme.typography.fontFamily,
    textAlign: 'center',
    marginBottom: theme.spacing.sm,
  },
  botao: {
    backgroundColor: theme.colors.brandBlue,
    borderRadius: theme.radius.control,
    minHeight: theme.control.minHeight,
    padding: theme.spacing.lg,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: theme.spacing.xs,
  },
  botaoTexto: {
    color: theme.colors.white,
    fontFamily: theme.typography.fontFamilySemiBold,
    fontSize: theme.fontSize.base,
  },
})
