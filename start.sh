#!/usr/bin/env bash
# Start Open Diagnostic Lab on macOS / Linux (requires Docker Desktop or Docker Engine).
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed. Install Docker Desktop from https://www.docker.com/products/docker-desktop/"
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "Docker is installed but not running. Start Docker Desktop, then run this script again."
  exit 1
fi

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example — change ADMIN_PASSWORD and SECRET_KEY before real patient data."
fi

echo "Building and starting (first run may take a few minutes)…"
docker compose up --build -d

PORT=$(grep -E '^WEB_PORT=' .env 2>/dev/null | cut -d= -f2 || true)
PORT=${PORT:-8080}

echo
echo "Open Diagnostic Lab is running."
echo "  UI:   http://localhost:${PORT}"
echo "  Login: see ADMIN_USERNAME / ADMIN_PASSWORD in .env"
echo
echo "Stop with:  ./stop.sh"
