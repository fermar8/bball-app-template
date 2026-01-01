@echo off
chcp 65001 >nul
echo Starting PostgreSQL test database...
docker-compose up -d postgres-test

echo Waiting for PostgreSQL to be ready...
timeout /t 5 /nobreak > nul

echo Setting environment variables...
set DB_HOST=localhost
set DB_PORT=5433
set DB_NAME=testdb
set DB_USER=testuser
set DB_PASSWORD=testpassword
set PGCLIENTENCODING=UTF8
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo Running integration tests...
.\venv\Scripts\python.exe -m pytest tests/integration/ -v

echo Stopping PostgreSQL test database...
docker-compose down

echo Done!
