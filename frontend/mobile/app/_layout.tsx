// Layout raiz do app mobile (Expo Router)
// Define a estrutura de navegação em Stack e configura a StatusBar

import { useEffect } from 'react'
import { Stack } from 'expo-router'
import * as SplashScreen from 'expo-splash-screen'
import { StatusBar } from 'expo-status-bar'
import { useFonts } from 'expo-font'

SplashScreen.preventAutoHideAsync()

export default function RootLayout() {
  const [fontsLoaded] = useFonts({
    Figtree: require('@expo-google-fonts/figtree/Figtree_400Regular.ttf'),
    'Figtree-SemiBold': require('@expo-google-fonts/figtree/Figtree_600SemiBold.ttf'),
    'Figtree-Bold': require('@expo-google-fonts/figtree/Figtree_700Bold.ttf'),
  })

  useEffect(() => {
    if (fontsLoaded) {
      SplashScreen.hideAsync()
    }
  }, [fontsLoaded])

  if (!fontsLoaded) return null

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
