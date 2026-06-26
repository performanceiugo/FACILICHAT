// Layout raiz do app mobile (Expo Router)
// Define a estrutura de navegação em Stack e configura a StatusBar

import { Stack } from 'expo-router'
import { StatusBar } from 'expo-status-bar'

export default function RootLayout() {
  return (
    <>
      {/* StatusBar com estilo automático (adapta ao tema claro/escuro do dispositivo) */}
      <StatusBar style="auto" />
      {/* Stack de navegação com headers ocultos — cada tela controla sua própria aparência */}
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="index" />           {/* Tela de redirecionamento inicial */}
        <Stack.Screen name="(auth)/login" />    {/* Tela de login */}
        <Stack.Screen name="(tabs)" />          {/* Navegação por abas (pós-login) */}
      </Stack>
    </>
  )
}
