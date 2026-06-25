import { Tabs } from 'expo-router'

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#1a56db',
        tabBarInactiveTintColor: '#6b7280',
        headerStyle: { backgroundColor: '#fff' },
        headerTitleStyle: { color: '#111827', fontWeight: '600' },
      }}
    >
      <Tabs.Screen
        name="chamados"
        options={{ title: 'Chamados', tabBarLabel: 'Chamados' }}
      />
      <Tabs.Screen
        name="perfil"
        options={{ title: 'Perfil', tabBarLabel: 'Perfil' }}
      />
    </Tabs>
  )
}
