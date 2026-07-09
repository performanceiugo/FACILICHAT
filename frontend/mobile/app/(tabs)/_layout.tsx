// Layout de navegacao por abas do app (pos-login)
// Define as duas abas principais: Chamados e Perfil.

import { Ionicons } from '@expo/vector-icons'
import { Tabs } from 'expo-router'
import { theme } from '@/lib/theme'

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: theme.colors.brandBlue,
        tabBarInactiveTintColor: theme.colors.ink500,
        tabBarStyle: { backgroundColor: theme.colors.surfaceCard, borderTopColor: theme.colors.borderSoft },
        tabBarLabelStyle: { fontFamily: theme.typography.fontFamilySemiBold },
        headerStyle: { backgroundColor: theme.colors.surfaceCard },
        headerTitleStyle: { color: theme.colors.ink900, fontFamily: theme.typography.fontFamilySemiBold },
      }}
    >
      <Tabs.Screen
        name="chamados"
        options={{
          title: 'Chamados',
          tabBarLabel: 'Chamados',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="chatbubble-ellipses-outline" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="perfil"
        options={{
          title: 'Perfil',
          tabBarLabel: 'Perfil',
          tabBarIcon: ({ color, size }) => <Ionicons name="person-outline" size={size} color={color} />,
        }}
      />
    </Tabs>
  )
}
