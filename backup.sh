#!/bin/bash
BACKUP_DIR="./backups"
RETENTION_DAYS=7

mkdir -p "$BACKUP_DIR"
DATE=$(date +%Y%m%d_%H%M%S)

docker run --rm \
  -v pet-project_pg_data:/source \
  -v "$(pwd)/$BACKUP_DIR:/backup" \
  alpine \
  tar czf "/backup/pg_$DATE.tar.gz" -C /source .

# Удаляем бэкапы старше RETENTION_DAYS
find "$BACKUP_DIR" -name "pg_*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup created: $BACKUP_DIR/pg_$DATE.tar.gz"
echo "Current backups:"
ls -lh "$BACKUP_DIR"
