// Entrada do painel administrativo.
// Redireciona o Gestor para a visao geral visual, mantendo /painel como URL curta e previsivel.

import { redirect } from 'next/navigation'

export default function PainelPage() {
  // A pagina raiz do painel nao tem conteudo proprio; ela leva direto ao resumo executivo.
  redirect('/painel/visao-geral')
}
