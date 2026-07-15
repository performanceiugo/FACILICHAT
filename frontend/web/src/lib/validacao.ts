// Validação nativa do navegador em português (item M13).
//
// Os balões de validação do HTML5 (`required`, `type="email"`) aparecem no idioma do NAVEGADOR,
// não do app — um Chrome em inglês mostra "Please include an '@' in the email address..." mesmo
// com a página inteira em português. `setCustomValidity` substitui o texto padrão pelos nossos,
// mantendo a validação nativa (o formulário continua bloqueando o submit sozinho, sem JS extra).
//
// Uso: <input ... onInvalid={aoInvalidarCampo} onInput={limparValidacaoCustomizada} />
// O onInput é obrigatório: enquanto houver customValidity setada o campo fica inválido para
// sempre — limpar ao digitar devolve a validação ao navegador para reavaliar o novo valor.

import type { FormEvent } from 'react'

// Traduz o motivo da invalidez (ValidityState) para uma mensagem em português.
export function aoInvalidarCampo(e: FormEvent<HTMLInputElement>) {
  const campo = e.currentTarget
  if (campo.validity.valueMissing) {
    campo.setCustomValidity('Preencha este campo.')
  } else if (campo.validity.typeMismatch && campo.type === 'email') {
    campo.setCustomValidity('Informe um e-mail válido (ex.: nome@dominio.com).')
  } else {
    // Qualquer outro motivo (pattern, min/max etc.) cai no genérico em português
    campo.setCustomValidity('Valor inválido.')
  }
}

// Limpa a mensagem customizada assim que o usuário digita, para o navegador revalidar o campo.
export function limparValidacaoCustomizada(e: FormEvent<HTMLInputElement>) {
  e.currentTarget.setCustomValidity('')
}
