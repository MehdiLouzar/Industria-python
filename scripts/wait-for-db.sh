#!/bin/bash
# scripts/wait-for-db.sh - Script d'attente pour la base de données

set -e

HOST="$1"
PORT="$2"
shift 2
CMD="$@"

echo "🔄 Waiting for PostgreSQL at $HOST:$PORT..."

# Fonction pour tester la connexion
test_connection() {
    nc -z "$HOST" "$PORT" > /dev/null 2>&1
}

# Fonction pour tester si la base de données est prête
test_database() {
    PGPASSWORD=postgres psql -h "$HOST" -p "$PORT" -U postgres -d industria -c "SELECT 1;" > /dev/null 2>&1
}

# Fonction pour vérifier si les tables existent
check_tables() {
    PGPASSWORD=postgres psql -h "$HOST" -p "$PORT" -U postgres -d industria -c "
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
    " -t | xargs
}

# Attendre que le port soit ouvert
echo "⏳ Step 1: Waiting for PostgreSQL port to be open..."
until test_connection; do
    echo "   Waiting for $HOST:$PORT..."
    sleep 2
done
echo "✅ Step 1: PostgreSQL port is open"

# Attendre que la base de données soit accessible
echo "⏳ Step 2: Waiting for database to accept connections..."
until test_database; do
    echo "   Waiting for database to accept connections..."
    sleep 2
done
echo "✅ Step 2: Database accepts connections"

# Attendre que les scripts d'initialisation soient terminés
echo "⏳ Step 3: Waiting for database initialization..."
RETRY_COUNT=0
MAX_RETRIES=30

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    TABLE_COUNT=$(check_tables)
    echo "   Found $TABLE_COUNT tables in database"
    
    if [ "$TABLE_COUNT" -gt 0 ]; then
        echo "✅ Step 3: Database initialization complete ($TABLE_COUNT tables found)"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "   Retry $RETRY_COUNT/$MAX_RETRIES - waiting for tables..."
    sleep 3
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "⚠️  Warning: Maximum retries reached, but continuing anyway"
fi

echo "🚀 Database is ready! Starting application..."
echo "   Command: $CMD"
exec $CMD