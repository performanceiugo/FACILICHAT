---
name: verificar-versoes
description: Audita as versões instaladas dos componentes do FaciliChat (Next.js, Expo/React/React Native, Node, Python, Docker Engine/Compose, PostgreSQL, Caddy, pacotes do backend) contra a versão mais recente/recomendada de cada um, e classifica cada item como Atual/Atenção/Crítico. Use quando o usuário pedir para checar se as dependências/versões estão desatualizadas, ou periodicamente como manutenção — não durante implementação normal de feature.
---

# Verificar versões — auditoria de atualidade de dependências

Skill de auditoria pontual: levanta a versão **instalada** de cada componente do FaciliChat e
compara com a versão **mais recente/recomendada** publicada pela fonte oficial. Ela só compara e
relata — não atualiza nada sozinha. Diferente de `verificar-seguranca` (que audita práticas de
segurança), aqui o foco é **atualidade de versão** (LTS/EOL, releases mais novos), não vulnerabilidade
conhecida (`npm audit`/`pip-audit` já cobrem isso automaticamente no projeto).

## Quando usar
- O usuário pede explicitamente para checar se as versões/dependências estão desatualizadas.
- Manutenção periódica (não é necessário rodar a cada sessão nem durante implementação de feature).

Não use durante o fluxo normal de implementação de uma feature — isso é auditoria de manutenção, não
verificação de API pontual (para isso existe `find-docs`/Context7, usado sob demanda).

## Componentes cobertos e onde ler a versão instalada
| Componente | Onde ler |
|---|---|
| Next.js, React, ESLint (web) | `frontend/web/package.json` |
| Expo, React Native, React (mobile) | `frontend/mobile/package.json` |
| Node local vs. Docker | `node --version`; `docker-compose.yml`/`docker-compose.prod.yml`/`Dockerfile` (imagem base) |
| Python local vs. Docker/CI | `python --version`; `Dockerfile` do backend; `.github/workflows/*.yml` |
| Pacotes do backend | `backend/requirements.txt` |
| PostgreSQL | `docker-compose.yml` (imagem do serviço `db`) |
| Caddy | `deploy/Caddyfile`/`docker-compose.prod.yml` |
| Docker Engine/Compose (máquina do usuário) | `docker --version`; `docker compose version` |

## Como usar
1. Rode os comandos acima para levantar as versões **instaladas** hoje. Não assuma valores antigos de
   memória — releia os arquivos e rode os comandos, pois isso muda com frequência.
2. Para a versão **mais recente/recomendada** de cada componente, use a fonte mais direta e barata:
   - Biblioteca específica com dúvida de API/breaking change → `find-docs` (Context7).
   - Release mais recente / política de suporte (LTS, EOL) de um runtime/ferramenta (Node, Python,
     Docker Engine, PostgreSQL, Next.js, Expo) → `WebSearch`/`WebFetch` na página oficial de releases
     ou de política de suporte.
   - Pacotes Python (`requirements.txt`) → pode rodar `pip list --outdated` dentro do container do
     backend (`docker compose exec backend pip list --outdated`) em vez de checar um por um na web.
3. Classifique cada componente:
   - **Atual** — última versão, ou dentro da mesma série com suporte ativo (ex.: LTS vigente).
   - **Atenção** — atrasado, mas ainda suportado/sem vulnerabilidade conhecida (não é urgente).
   - **Crítico** — vulnerabilidade conhecida, fim de suporte (EOL) próximo/passado, ou breaking change
     de segurança represado.
4. Monte a tabela final: `Componente | Instalado | Mais recente/recomendado | Classificação | Fonte`.
5. **Cada componente Atenção/Crítico que ainda não está no plano vira um item novo** — siga a Regra de
   Ouro do `CLAUDE.md`: antes de adicionar, avise o usuário (arquivo, item, motivo) e peça confirmação
   explícita; só então edite `docs/plano-implementacao.md` (`[ ]`, na fase/seção que fizer sentido) e
   crie a subtarefa correspondente no ClickUp (list `901114027434`) com o `CU:` novo.
6. Não implemente nenhuma atualização nesta skill — ela só gera a lista e, com confirmação, registra
   os itens no plano. A implementação de cada atualização é um item separado, seguindo a fila normal.

## Saída
Tabela compacta por componente + lista dos itens novos que foram (ou serão, após confirmação)
adicionados ao plano. Não é necessário relatório extenso.
