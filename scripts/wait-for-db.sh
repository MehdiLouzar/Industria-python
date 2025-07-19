#!/bin/bash
# scripts/wait-for-db.sh - wait for PostgreSQL then run the given command
set -e

HOST="$1"
PORT="$2"
shift 2
CMD="$@"

echo "🔄 Waiting for PostgreSQL at $HOST:$PORT..."

# Test if the port is open
until nc -z "$HOST" "$PORT" >/dev/null 2>&1; do
    echo "   Waiting for $HOST:$PORT..."
    sleep 2
done

echo "✅ PostgreSQL port is open"

# Wait for the server to accept connections
until PGPASSWORD=postgres psql -h "$HOST" -p "$PORT" -U postgres -d industria -c "SELECT 1;" >/dev/null 2>&1; do
    echo "   Waiting for database to accept connections..."
    sleep 2
done

echo "✅ Database accepts connections"

exec $CMD

