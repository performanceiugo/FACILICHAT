'use client'

// Hook generico de "atualizacao automatica" (estilo painel de BI) — item novo do plano (Fase 4).
// Reexecuta `buscar` a cada `intervaloMs` enquanto a aba estiver visivel, e pausa quando ela vai
// para segundo plano (Page Visibility API) para nao gastar requisicoes com o usuario fora da tela.
// Ao voltar a ficar visivel, busca na hora em vez de esperar o proximo tick do intervalo.
//
// Decisao de escopo (confirmada com o usuario): polling simples, sem SWR/React Query — a pagina
// que usa o hook decide o que fazer com o resultado (ex.: nao reexibir o "Carregando..." em
// atualizacoes de fundo, so na carga inicial).

import { useEffect, useRef } from 'react'

export function useAtualizacaoPeriodica(buscar: () => void, intervaloMs = 20000) {
  // Guarda a funcao mais recente numa ref para o efeito abaixo nao precisar recriar o
  // setInterval a cada render (evita reiniciar o timer quando `buscar` muda de referencia).
  // A escrita roda num efeito (nao direto no corpo da render) porque o Next.js 16/React Compiler
  // ESLint (`react-hooks/refs`) proibe mutar `ref.current` durante a render.
  const buscarRef = useRef(buscar)
  useEffect(() => {
    buscarRef.current = buscar
  })

  useEffect(() => {
    // Tick do polling: so busca se a aba estiver visivel — evita gastar requisicao com o
    // usuario em outra aba/janela (o listener de visibilitychange abaixo cobre o "voltou a olhar").
    const intervalo = setInterval(() => {
      if (document.visibilityState === 'visible') buscarRef.current()
    }, intervaloMs)

    // Ao voltar a ficar visivel, busca imediatamente em vez de esperar o proximo tick do
    // intervalo — senao os dados poderiam ficar ate `intervaloMs` desatualizados na volta.
    function aoVisibilidadeMudar() {
      if (document.visibilityState === 'visible') buscarRef.current()
    }
    document.addEventListener('visibilitychange', aoVisibilidadeMudar)

    return () => {
      clearInterval(intervalo)
      document.removeEventListener('visibilitychange', aoVisibilidadeMudar)
    }
  }, [intervaloMs])
}
