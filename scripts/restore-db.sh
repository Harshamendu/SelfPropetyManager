#!/bin/bash
# Restore PostgreSQL database from backup
# Usage: ./scripts/restore-db.sh [backup_file]
#   If no file specified, uses the latest backup

BACKUP_DIR="${HOME}/Documents/PropertyManager/backups"

if [ -n "$1" ]; then
    BACKUP_FILE="$1"
else
    BACKUP_FILE=$(ls -t "$BACKUP_DIR"/propmanager_*.sql 2>/dev/null | head -1)
fi

if [ -z "$BACKUP_FILE" ] || [ ! -f "$BACKUP_FILE" ]; then
    echo "ERROR: No backup file found"
    echo "Usage: $0 [path/to/backup.sql]"
    exit 1
fi

echo "Restoring from: $BACKUP_FILE"
echo "WARNING: This will overwrite the current database!"
read -p "Continue? (y/N): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Cancelled."
    exit 0
fi

# Drop and recreate database, then restore
docker-compose exec -T db psql -U propmanager -d postgres -c "DROP DATABASE IF EXISTS propmanager;"
docker-compose exec -T db psql -U propmanager -d postgres -c "CREATE DATABASE propmanager;"
docker-compose exec -T db psql -U propmanager propmanager < "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "Restore completed successfully!"
else
    echo "ERROR: Restore failed!"
    exit 1
fi
