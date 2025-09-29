#!/bin/bash

# Script de Despliegue - Sistema de Control de Facturas Boosting
# Uso: ./scripts/deploy.sh [environment]
# Ejemplo: ./scripts/deploy.sh production

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

# Verificar argumentos
ENVIRONMENT=${1:-development}

log "🚀 Iniciando despliegue en entorno: $ENVIRONMENT"

# Verificar que Docker esté instalado
if ! command -v docker &> /dev/null; then
    error "Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

# Verificar que Docker Compose esté instalado
if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose no está instalado. Por favor instala Docker Compose primero."
    exit 1
fi

# Verificar archivo .env
if [ ! -f .env ]; then
    warning "Archivo .env no encontrado. Copiando desde env.example..."
    cp env.example .env
    warning "Por favor configura las variables en .env antes de continuar."
    exit 1
fi

# Crear directorios necesarios
log "📁 Creando directorios necesarios..."
mkdir -p backend/uploads
mkdir -p backend/logs
mkdir -p nginx/ssl

# Verificar credenciales de Gmail API
if [ ! -f backend/credentials.json ]; then
    warning "Archivo credentials.json no encontrado en backend/"
    warning "La funcionalidad de Gmail API no estará disponible."
fi

# Construir imágenes Docker
log "🔨 Construyendo imágenes Docker..."
docker-compose build --no-cache

# Detener servicios existentes
log "🛑 Deteniendo servicios existentes..."
docker-compose down

# Iniciar servicios
log "🚀 Iniciando servicios..."
if [ "$ENVIRONMENT" = "production" ]; then
    docker-compose --profile production up -d
else
    docker-compose up -d
fi

# Esperar a que los servicios estén listos
log "⏳ Esperando a que los servicios estén listos..."
sleep 30

# Verificar salud de los servicios
log "🏥 Verificando salud de los servicios..."

# Verificar base de datos
if docker-compose exec -T db pg_isready -U boosting_user -d facturas_boosting > /dev/null 2>&1; then
    success "✅ Base de datos: OK"
else
    error "❌ Base de datos: ERROR"
    exit 1
fi

# Verificar backend
if curl -f -s http://localhost:8000/health > /dev/null; then
    success "✅ Backend: OK"
else
    error "❌ Backend: ERROR"
    exit 1
fi

# Verificar frontend
if curl -f -s http://localhost/ > /dev/null; then
    success "✅ Frontend: OK"
else
    error "❌ Frontend: ERROR"
    exit 1
fi

# Ejecutar migraciones
log "🗄️ Ejecutando migraciones de base de datos..."
docker-compose exec -T backend alembic upgrade head

# Verificar estado final
log "📊 Estado final de los servicios:"
docker-compose ps

success "🎉 ¡Despliegue completado exitosamente!"
log "🌐 Frontend: http://localhost"
log "🔧 Backend API: http://localhost:8000"
log "📚 Documentación API: http://localhost:8000/docs"

# Mostrar logs si hay errores
if [ "$ENVIRONMENT" = "development" ]; then
    log "📋 Para ver logs en tiempo real: docker-compose logs -f"
    log "🛑 Para detener servicios: docker-compose down"
fi
