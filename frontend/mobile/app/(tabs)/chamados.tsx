// Tela de listagem de chamados do app mobile
// Suporta pull-to-refresh (puxar para atualizar) para recarregar a lista

import { useEffect, useRef, useState } from 'react'
import { View, Text, FlatList, StyleSheet, ActivityIndicator, RefreshControl, TouchableOpacity } from 'react-native'
import { api } from '@/lib/api'
import type { Chamado } from '@/lib/types'
import { theme } from '@/lib/theme'

// Labels amigáveis para exibição dos status no card
const STATUS_LABEL: Record<string, string> = {
  Recebido: 'Recebido',
  EmAndamento: 'Em Andamento',
  Agendado: 'Agendado',
  Concluido: 'Concluído',
  Cancelado: 'Cancelado',
}

// Cores de destaque para cada nível de prioridade
const PRIORIDADE_COR: Record<string, string> = {
  Baixa: theme.colors.success,
  Media: theme.colors.warning,
  Alta: theme.colors.danger,
  Critica: theme.colors.dangerStrong,
}

export default function ChamadosScreen() {
  const [chamados, setChamados] = useState<Chamado[]>([])
  const [carregando, setCarregando] = useState(true)
  const [recarregando, setRecarregando] = useState(false)  // true durante pull-to-refresh
  const [erro, setErro] = useState('')
  // Item B2: guarda de montagem — evita setState após sair da tela antes da API responder
  // (troca rápida de aba ou pull-to-refresh seguido de saída da tela).
  const montadoRef = useRef(true)

  // Busca os chamados da API — reutilizada tanto no mount quanto no pull-to-refresh
  async function carregar() {
    try {
      setErro('')
      const dados = await api.chamados.listar()
      if (montadoRef.current) setChamados(dados)
    } catch (err) {
      if (montadoRef.current) setErro(err instanceof Error ? err.message : 'Erro ao carregar chamados')
    } finally {
      if (montadoRef.current) {
        setCarregando(false)
        setRecarregando(false)
      }
    }
  }

  // Carrega ao abrir a tela
  useEffect(() => {
    montadoRef.current = true
    carregar()
    return () => { montadoRef.current = false }
  }, [])

  // Spinner de carregamento inicial (tela cheia)
  if (carregando) {
    return (
      <View style={s.centro}>
        <ActivityIndicator size="large" color={theme.colors.brandBlue} />
      </View>
    )
  }

  if (erro) {
    return (
      <View style={s.centro}>
        <Text style={s.erro}>{erro}</Text>
        <TouchableOpacity style={s.botaoRetry} onPress={carregar}>
          <Text style={s.botaoRetryTexto}>Tentar novamente</Text>
        </TouchableOpacity>
      </View>
    )
  }

  return (
    <FlatList
      data={chamados}
      keyExtractor={item => item.ID}
      contentContainerStyle={s.lista}
      // Pull-to-refresh: arrasta para baixo para recarregar a lista
      refreshControl={
        <RefreshControl
          refreshing={recarregando}
          onRefresh={() => { setRecarregando(true); carregar() }}
          tintColor={theme.colors.brandBlue}
        />
      }
      ListEmptyComponent={<Text style={s.vazio}>Nenhum chamado encontrado.</Text>}
      // Card de cada chamado na lista
      renderItem={({ item }) => (
        <View style={s.card}>
          {/* Topo: categoria à esquerda, fila à direita */}
          <View style={s.cardTopo}>
            <Text style={s.categoria}>{item.Categoria}</Text>
            <Text style={s.fila}>{item.Fila}</Text>
          </View>
          {item.Resumo && <Text style={s.resumo}>{item.Resumo}</Text>}
          {/* Rodapé: status e prioridade colorida */}
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

// Estilos dos cards e da lista
const s = StyleSheet.create({
  centro: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: theme.spacing.xl,
    backgroundColor: theme.colors.surfacePage,
  },
  lista: {
    padding: theme.spacing.lg,
    gap: theme.spacing.md,
    backgroundColor: theme.colors.surfacePage,
  },
  vazio: {
    textAlign: 'center',
    color: theme.colors.ink500,
    marginTop: theme.spacing.xxl,
    fontFamily: theme.typography.fontFamily,
  },
  erro: {
    color: theme.colors.danger,
    fontFamily: theme.typography.fontFamily,
    marginBottom: theme.spacing.md,
    textAlign: 'center',
  },
  botaoRetry: {
    backgroundColor: theme.colors.brandBlue,
    borderRadius: theme.radius.control,
    minHeight: theme.control.minHeight,
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.md,
    justifyContent: 'center',
  },
  botaoRetryTexto: {
    color: theme.colors.white,
    fontFamily: theme.typography.fontFamilySemiBold,
  },
  card: {
    backgroundColor: theme.colors.surfaceCard,
    borderRadius: theme.radius.card,
    padding: theme.spacing.lg,
    borderWidth: 1,
    borderColor: theme.colors.borderSoft,
    gap: theme.spacing.sm,
  },
  cardTopo: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  categoria: { fontFamily: theme.typography.fontFamilySemiBold, fontSize: theme.fontSize.md, color: theme.colors.ink900 },
  fila: {
    fontSize: theme.fontSize.xs,
    color: theme.colors.ink500,
    backgroundColor: theme.colors.brandBlueSoft,
    paddingHorizontal: theme.spacing.sm,
    paddingVertical: 3,
    borderRadius: theme.radius.pill,
    fontFamily: theme.typography.fontFamily,
  },
  resumo: { fontSize: theme.fontSize.sm, color: theme.colors.ink500, fontFamily: theme.typography.fontFamily },
  cardRodape: { flexDirection: 'row', alignItems: 'center', gap: theme.spacing.md },
  status: {
    fontSize: theme.fontSize.xs,
    backgroundColor: theme.colors.surfacePage,
    paddingHorizontal: theme.spacing.sm,
    paddingVertical: 3,
    borderRadius: theme.radius.pill,
    color: theme.colors.ink700,
    fontFamily: theme.typography.fontFamily,
  },
  prioridade: { fontSize: theme.fontSize.xs, fontFamily: theme.typography.fontFamilyBold },
})
