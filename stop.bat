@echo off
cd /d "%~dp0"
docker compose down
echo Stopped. Database files remain in the Docker volume.
pause
