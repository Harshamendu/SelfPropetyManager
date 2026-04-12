#!/bin/bash
# Backup PostgreSQL database from Docker container
# Usage: ./scripts/backup-db.sh

BACKUP_DIR="${HOME}/Documents/PropertyManager/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/propmanager_${TIMESTAMP}.sql"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Run pg_dump inside the db container
docker-compose exec -T db pg_dump -U propmanager propmanager > "$BACKUP_FILE"

if [ $? -eq 0 ] && [ -s "$BACKUP_FILE" ]; then
    echo "Backup saved to: $BACKUP_FILE"
    echo "Size: $(du -h "$BACKUP_FILE" | cut -f1)"

    # Keep only last 5 backups
    ls -t "$BACKUP_DIR"/propmanager_*.sql 2>/dev/null | tail -n +6 | xargs -r rm
    echo "Cleanup: keeping last 5 backups"
else
    echo "ERROR: Backup failed!"
    rm -f "$BACKUP_FILE"
    exit 1
fi
