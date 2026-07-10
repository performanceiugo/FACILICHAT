#!/usr/bin/env bash
# Backup diário do Postgres de produção do FaciliChat (item S9).
# Gera um dump completo comprimido em ./backups e, se BACKUP_RCLONE_DESTINO estiver
# configurado no .env, envia uma cópia para o armazenamento EXTERNO (fora do VPS) —
# um backup que mora no mesmo disco do banco não sobrevive à falha desse disco.
#
# Uso manual:     ./deploy/backup-banco.sh
# Agendamento:    crontab -e   →   0 3 * * * /caminho/FACILICHAT/deploy/backup-banco.sh >> /var/log/facilichat-backup.log 2>&1
# Restauração:    ver "Backup e restauração" em docs/deploy-producao.md
#
# Pré-requisitos no VPS: docker compose de produção no ar; rclone instalado e com o
# remote configurado (`rclone config`) se quiser a cópia externa.

set -euo pipefail

# Raiz do projeto = pasta acima deste script (permite rodar de qualquer diretório, ex.: cron)
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"

# Carrega as variáveis do .env de produção (POSTGRES_*, BACKUP_*)
if [[ ! -f .env ]]; then
    echo "ERRO: .env não encontrado em $RAIZ (modelo: .env.prod.example)" >&2
    exit 1
fi
set -a            # exporta tudo que o source definir
source .env
set +a

RETENCAO_DIAS="${BACKUP_RETENCAO_DIAS:-7}"
PASTA_BACKUPS="$RAIZ/backups"
CARIMBO="$(date +%Y-%m-%d_%H%M)"
ARQUIVO="$PASTA_BACKUPS/facilichat_${CARIMBO}.sql.gz"

mkdir -p "$PASTA_BACKUPS"

# Dump completo do banco de dentro do container (pg_dump da mesma versão do servidor),
# comprimido no caminho. `-T` desabilita o TTY (necessário para rodar via cron).
echo "[backup] gerando dump: $ARQUIVO"
docker compose -f docker-compose.prod.yml exec -T db \
    pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" | gzip > "$ARQUIVO"

# Um dump de banco recém-criado tem alguns KB; menor que isso é sinal de falha silenciosa
if [[ ! -s "$ARQUIVO" ]]; then
    echo "ERRO: dump vazio — backup FALHOU" >&2
    exit 1
fi
echo "[backup] dump ok ($(du -h "$ARQUIVO" | cut -f1))"

# Cópia externa via rclone (só se o destino estiver configurado no .env)
if [[ -n "${BACKUP_RCLONE_DESTINO:-}" ]]; then
    echo "[backup] enviando cópia externa para $BACKUP_RCLONE_DESTINO"
    rclone copy "$ARQUIVO" "$BACKUP_RCLONE_DESTINO"
    echo "[backup] cópia externa ok"
else
    echo "[backup] AVISO: BACKUP_RCLONE_DESTINO vazio — backup ficou SÓ no VPS (configure a cópia externa!)"
fi

# Retenção local: apaga dumps com mais de N dias (as cópias externas não são tocadas)
find "$PASTA_BACKUPS" -name 'facilichat_*.sql.gz' -mtime +"$RETENCAO_DIAS" -delete

echo "[backup] concluído em $(date '+%Y-%m-%d %H:%M:%S')"
