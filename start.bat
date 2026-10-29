@echo off
REM Start Open Diagnostic Lab on Windows (requires Docker Desktop).
cd /d "%~dp0"

where docker >nul 2>nul
if errorlevel 1 (
  echo Docker is not installed. Install Docker Desktop from:
  echo https://www.docker.com/products/docker-desktop/
  pause
  exit /b 1
)

docker info >nul 2>nul
if errorlevel 1 (
  echo Docker is not running. Start Docker Desktop, then run start.bat again.
  pause
  exit /b 1
)

if not exist .env (
  copy .env.example .env >nul
  echo Created .env from .env.example - change passwords before real patient data.
)

echo Building and starting (first run may take a few minutes)...
docker compose up --build -d
if errorlevel 1 (
  echo Failed to start. Ensure Docker Desktop is running and WSL2 is enabled.
  pause
  exit /b 1
)

echo.
echo Open Diagnostic Lab is running.
echo   UI: http://localhost:8080
echo   Login: see ADMIN_USERNAME / ADMIN_PASSWORD in .env
echo.
echo Stop with: stop.bat
pause
