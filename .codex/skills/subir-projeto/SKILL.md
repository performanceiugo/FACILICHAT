<!-- Arquivo de cabeçalho: runbook local para levantar o FaciliChat sem depender de memória implícita do agente. -->
---
name: subir-projeto
description: Levanta banco, backend e frontend web do FaciliChat para validação local.
---

# Subir o FaciliChat

## Ordem

1. Verificar `docker compose version`, `docker ps` e `node --version`.
2. Garantir `frontend/web/.env.local` apontando para `http://localhost:8000`.
3. Rodar `docker compose up -d --build` na raiz.
4. Esperar a API responder em `http://localhost:8000/`.
5. Semear a primeira Empresa/Gestor com `backend/scripts/criar_empresa.py`, se necessário.
6. Rodar `npm run dev` em `frontend/web`.
7. Validar `http://localhost:3000/login` e `http://localhost:8000/docs`.

## Avisos

- O mobile fica fora do fluxo padrão.
- Se rede, Docker ou escrita fora do workspace forem necessários, o Codex deve pedir permissão.
