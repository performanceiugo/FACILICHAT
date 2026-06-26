// Layout de navegação por abas do app (pós-login)
// Define as duas abas principais: Chamados e Perfil

import { Tabs } from 'expo-router'

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#1a56db',    // Cor da aba selecionada (azul primário)
        tabBarInactiveTintColor: '#6b7280',  // Cor das abas inativas (cinza)
        headerStyle: { backgroundColor: '#fff' },
        headerTitleStyle: { color: '#111827', fontWeight: '600' },
      }}
    >
      {/* Aba de listagem de chamados */}
      <Tabs.Screen
        name="chamados"
        options={{ title: 'Chamados', tabBarLabel: 'Chamados' }}
      />
      {/* Aba de perfil e logout */}
      <Tabs.Screen
        name="perfil"
        options={{ title: 'Perfil', tabBarLabel: 'Perfil' }}
      />
    </Tabs>
  )
}
