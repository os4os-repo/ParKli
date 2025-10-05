#!/bin/bash

# Name des Docker-Containers in dem die Influx-DB liegt
CONTAINER_NAME="influxdb"

# Zielverzeichnis im Container in dem das Influx DMBS das Backup schreiben soll
BACKUP_DIR="/mnt/backups"

# Pfad zum Hostvolumen welches in den Container durch-gemapped wird
HOSTVOL_DIR=""

# Datum im Format YYYY-MM-DD
DATE=$(date +%F)

# Backup-Dateiname
BACKUP_NAME="${CONTAINER_NAME}_full_backup_$DATE"

# ZIP-Dateiname
ZIP_NAME="${BACKUP_NAME}.zip"

# ZIP-Zielordner
ZIP_PATH="/tmp"

# ZIP-Passwort
ZIP_PASSWORD=""  # unbedingt ändern!

# Backup ausführen innerhalb des Containers
docker exec $CONTAINER_NAME influx backup /mnt/backups/$BACKUP_NAME

if [ $? -ne 0 ]; then
    echo "InfluxDB Backup fehlgeschlagen!"
    exit 1
fi

# === Backup in verschlüsselte ZIP packen ===
zip -r -P "$ZIP_PASSWORD" "$ZIP_PATH/$ZIP_NAME" "$HOSTVOL_DIR/$BACKUP_NAME"
if [ $? -eq 0 ]; then
    echo "Backup erfolgreich verschlüsselt: $ZIP_NAME"
    # Optional: unverschlüsseltes Backup löschen
    rm -rf "$HOSTVOL_DIR/$BACKUP_NAME"
else
    echo "Fehler beim Erstellen der verschlüsselten ZIP!"
    exit 1
fi
