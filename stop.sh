#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
docker compose down
echo "Stopped. Database files remain in the Docker volume (data is kept)."
