#!/usr/bin/env bash
# Script to run integration tests with Docker PostgreSQL

set -e

echo "Starting PostgreSQL test database..."
docker-compose up -d postgres-test

echo "Waiting for PostgreSQL to be ready..."
timeout=30
elapsed=0
until docker-compose exec -T postgres-test pg_isready -U testuser -d testdb > /dev/null 2>&1; do
    if [ $elapsed -ge $timeout ]; then
        echo "Timeout waiting for PostgreSQL"
        exit 1
    fi
    echo "Waiting... ($elapsed/$timeout seconds)"
    sleep 2
    elapsed=$((elapsed + 2))
done

echo "PostgreSQL is ready!"
echo "Running integration tests..."

# Load test environment variables
export $(grep -v '^#' .env.test | xargs)

# Run integration tests
pytest tests/integration/ -v

echo "Stopping PostgreSQL test database..."
docker-compose down
