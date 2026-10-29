#!/usr/bin/env bash
# Backup PostgreSQL data from the Compose stack into ./backups/
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

mkdir -p backups
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="backups/diagnostic_lab_${STAMP}.sql.gz"

USER_NAME="${POSTGRES_USER:-lab}"
DB_NAME="${POSTGRES_DB:-diagnostic_lab}"

echo "Creating backup ${OUT}…"
docker compose exec -T db pg_dump -U "$USER_NAME" "$DB_NAME" | gzip > "$OUT"
echo "Done: ${OUT}"
echo "Store this file on encrypted, clinic-controlled media. Do not upload to public cloud without a DPA."
