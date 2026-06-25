import { useEffect, useState } from 'react'
import { View, Text, FlatList, StyleSheet, ActivityIndicator, RefreshControl } from 'react-native'
import { api } from '@/lib/api'
import type { Chamado } from '@/lib/types'

const STATUS_LABEL: Record<string, string> = {
  Recebido: 'Recebido',
  EmAndamento: 'Em Andamento',
  Agendado: 'Agendado',
  Concluido: 'Concluído',
  Cancelado: 'Cancelado',
}

const PRIORIDADE_COR: Record<string, string> = {
  Baixa: '#16a34a',
  Media: '#d97706',
  Alta: '#dc2626',
  Critica: '#7c3aed',
}

export default function ChamadosScreen() {
  const [chamados, setChamados] = useState<Chamado[]>([])
  const [carregando, setCarregando] = useState(true)
  const [recarregando, setRecarregando] = useState(false)

  async function carregar() {
    try {
      const dados = await api.chamados.listar()
      setChamados(dados)
    } finally {
      setCarregando(false)
      setRecarregando(false)
    }
  }

  useEffect(() => { carregar() }, [])

  if (carregando) {
    return (
      <View style={s.centro}>
        <ActivityIndicator size="large" color="#1a56db" />
      </View>
    )
  }

  return (
    <FlatList
      data={chamados}
      keyExtractor={item => item.ID}
      contentContainerStyle={s.lista}
      refreshControl={
        <RefreshControl
          refreshing={recarregando}
          onRefresh={() => { setRecarregando(true); carregar() }}
          tintColor="#1a56db"
        />
      }
      ListEmptyComponent={<Text style={s.vazio}>Nenhum chamado encontrado.</Text>}
      renderItem={({ item }) => (
        <View style={s.card}>
          <View style={s.cardTopo}>
            <Text style={s.categoria}>{item.Categoria}</Text>
            <Text style={s.fila}>{item.Fila}</Text>
          </View>
          {item.Resumo && <Text style={s.resumo}>{item.Resumo}</Text>}
          <View style={s.cardRodape}>
            <Text style={s.status}>{STATUS_LABEL[item.Status]}</Text>
            <Text style={[s.prioridade, { color: PRIORIDADE_COR[item.Prioridade] }]}>
              {item.Prioridade}
            </Text>
          </View>
        </View>
      )}
    />
  )
}

const s = StyleSheet.create({
  centro: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  lista: { padding: 16, gap: 10 },
  vazio: { textAlign: 'center', color: '#6b7280', marginTop: 40 },
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    gap: 8,
  },
  cardTopo: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  categoria: { fontWeight: '600', fontSize: 15, color: '#111827' },
  fila: {
    fontSize: 12,
    color: '#6b7280',
    backgroundColor: '#f3f4f6',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 999,
  },
  resumo: { fontSize: 14, color: '#6b7280' },
  cardRodape: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  status: {
    fontSize: 12,
    backgroundColor: '#f3f4f6',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 999,
    color: '#374151',
  },
  prioridade: { fontSize: 13, fontWeight: '700' },
})
