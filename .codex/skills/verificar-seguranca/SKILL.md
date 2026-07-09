<!-- Arquivo de cabeçalho: orienta o Codex a auditar segurança técnica só quando a alteração tocar autenticação, sessão, CORS, cookies, JWT ou RLS. -->
---
name: verificar-seguranca
description: Compara a segurança técnica atual do projeto com documentação recente antes de mexer em autenticação, cookies, JWT, CORS, headers ou isolamento multi-tenant.
---

# Verificar segurança

## Quando usar

Use apenas se a mudança tocar:

- autenticação
- sessão/cookies
- JWT
- CORS
- headers HTTP de segurança
- RLS ou isolamento por `EmpresaID`

## Passos

1. Leia o código atual afetado.
2. Identifique o tema exato da revisão.
3. Busque documentação oficial atual só para esse tema.
4. Compare estado atual e recomendação.
5. Classifique cada item como `OK`, `ATENCAO` ou `CRITICO`.

## Saída esperada

Use o formato:

`Tema | Estado atual | Recomendação | Classificação`

## Regra de parada

Se aparecer `ATENCAO` ou `CRITICO`, isso vira mudança de política de segurança:
registrar no plano e pedir confirmação antes de alterar código.
