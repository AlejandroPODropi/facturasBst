#!/bin/bash

# Script de Backup - Sistema de Control de Facturas Boosting
# Uso: ./scripts/backup.sh

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Configuración
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_BACKUP_FILE="facturas_db_${DATE}.sql"
UPLOADS_BACKUP_FILE="facturas_uploads_${DATE}.tar.gz"
LOGS_BACKUP_FILE="facturas_logs_${DATE}.tar.gz"

log "🔄 Iniciando proceso de backup..."

# Crear directorio de backup
mkdir -p "$BACKUP_DIR"

# Verificar que Docker esté ejecutándose
if ! docker-compose ps | grep -q "Up"; then
    error "Los servicios Docker no están ejecutándose. Inicia los servicios primero."
    exit 1
fi

# Backup de base de datos
log "🗄️ Realizando backup de base de datos..."
if docker-compose exec -T db pg_dump -U boosting_user -d facturas_boosting > "$BACKUP_DIR/$DB_BACKUP_FILE"; then
    success "✅ Backup de base de datos completado: $DB_BACKUP_FILE"
else
    error "❌ Error en backup de base de datos"
    exit 1
fi

# Backup de archivos de uploads
log "📁 Realizando backup de archivos de uploads..."
if tar -czf "$BACKUP_DIR/$UPLOADS_BACKUP_FILE" -C backend uploads/ 2>/dev/null; then
    success "✅ Backup de uploads completado: $UPLOADS_BACKUP_FILE"
else
    warning "⚠️ No se encontraron archivos de uploads para respaldar"
fi

# Backup de logs
log "📋 Realizando backup de logs..."
if tar -czf "$BACKUP_DIR/$LOGS_BACKUP_FILE" -C backend logs/ 2>/dev/null; then
    success "✅ Backup de logs completado: $LOGS_BACKUP_FILE"
else
    warning "⚠️ No se encontraron logs para respaldar"
fi

# Backup de configuración
log "⚙️ Realizando backup de configuración..."
CONFIG_BACKUP_FILE="facturas_config_${DATE}.tar.gz"
tar -czf "$BACKUP_DIR/$CONFIG_BACKUP_FILE" \
    .env \
    docker-compose.yml \
    backend/credentials.json \
    backend/token.json \
    2>/dev/null || warning "⚠️ Algunos archivos de configuración no se encontraron"

# Crear archivo de información del backup
INFO_FILE="$BACKUP_DIR/backup_info_${DATE}.txt"
cat > "$INFO_FILE" << EOF
Backup realizado el: $(date)
Sistema: Control de Facturas Boosting
Versión: 1.0.0

Archivos incluidos:
- Base de datos: $DB_BACKUP_FILE
- Uploads: $UPLOADS_BACKUP_FILE
- Logs: $LOGS_BACKUP_FILE
- Configuración: $CONFIG_BACKUP_FILE

Tamaños:
$(ls -lh "$BACKUP_DIR"/*_${DATE}.* 2>/dev/null | awk '{print $5, $9}')

Para restaurar:
1. Detener servicios: docker-compose down
2. Restaurar base de datos: docker-compose exec -T db psql -U boosting_user -d facturas_boosting < $DB_BACKUP_FILE
3. Restaurar archivos: tar -xzf $UPLOADS_BACKUP_FILE -C backend/
4. Reiniciar servicios: docker-compose up -d
EOF

success "✅ Backup completado exitosamente"
log "📁 Archivos de backup guardados en: $BACKUP_DIR"
log "📋 Información del backup: $INFO_FILE"

# Mostrar resumen
log "📊 Resumen del backup:"
ls -lh "$BACKUP_DIR"/*_${DATE}.*

# Limpiar backups antiguos (mantener últimos 7 días)
log "🧹 Limpiando backups antiguos..."
find "$BACKUP_DIR" -name "*.sql" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.txt" -mtime +7 -delete

success "🎉 Proceso de backup completado"
