# Take Open Diagnostic Lab to your personal PC

This project is already packaged for sharing: **one folder + Docker**. No cloud account is required. Patient data stays on the PC that runs it.

## What you need on the personal PC

1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) for **Windows** or **Mac**  
   (or Docker Engine + Compose on Linux)
2. About **2 GB** free disk for images on first start
3. This project folder (zip or git clone)

## Option A — Zip (simplest)

1. Copy `open-diagnostic-lab.zip` to your PC (USB, email to yourself, cloud drive, `scp`, etc.).
2. Unzip it.
3. On **Windows**: double-click `start.bat`  
   On **Mac/Linux**: open Terminal in the folder and run:
   ```bash
   chmod +x start.sh stop.sh scripts/backup.sh
   ./start.sh
   ```
4. Browser: **http://localhost:8080**
5. Sign in with credentials from `.env` (created automatically from `.env.example` on first start).

## Option B — GitHub / GitLab (best for updates)

On this machine (or any copy of the project):

```bash
cd diagnostic-lab
git init -b main
git add .
git commit -m "Open Diagnostic Lab self-hosted MVP"
# Create an empty repo on GitHub, then:
git remote add origin https://github.com/YOUR_USER/open-diagnostic-lab.git
git push -u origin main
```

On your personal PC:

```bash
git clone https://github.com/YOUR_USER/open-diagnostic-lab.git
cd open-diagnostic-lab
./start.sh          # or start.bat on Windows
```

Do **not** commit `.env` (it is gitignored). Each PC creates its own `.env`.

## After first start — security checklist

Edit `.env` and change at least:

- `SECRET_KEY`
- `POSTGRES_PASSWORD`
- `ADMIN_PASSWORD`

Then restart:

```bash
docker compose up -d
```

## Backup on your PC

```bash
./scripts/backup.sh    # Mac/Linux with Docker
```

On Windows (PowerShell in the project folder):

```powershell
docker compose exec -T db pg_dump -U lab diagnostic_lab | Out-File -Encoding utf8 backup.sql
```

## Sharing with others (open source)

- Share the **source zip** or **git repo**, not your `.env` and not database dumps that contain real patients.
- License is Apache-2.0 — see `LICENSE`, `PRIVACY.md`, `SECURITY.md`.

## Troubleshooting

| Problem | Fix |
|--------|-----|
| Port 8080 in use | Set `WEB_PORT=8081` in `.env`, restart |
| Docker not running | Start Docker Desktop and wait until it says running |
| Windows containers error | In Docker Desktop, switch to **Linux containers** |
| Blank page / API errors | `docker compose logs api` and check containers are healthy |
