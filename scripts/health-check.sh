#!/bin/bash

# Script de Health Check - Sistema de Control de Facturas Boosting
# Uso: ./scripts/health-check.sh

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
BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost"
DB_CONTAINER="facturas_db"
BACKEND_CONTAINER="facturas_backend"
FRONTEND_CONTAINER="facturas_frontend"

log "🏥 Iniciando health check del sistema..."

# Función para verificar HTTP endpoint
check_http() {
    local url=$1
    local name=$2
    
    if curl -f -s --max-time 10 "$url" > /dev/null; then
        success "✅ $name: OK ($url)"
        return 0
    else
        error "❌ $name: ERROR ($url)"
        return 1
    fi
}

# Función para verificar contenedor Docker
check_container() {
    local container=$1
    local name=$2
    
    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "$container.*Up"; then
        success "✅ $name: OK (contenedor ejecutándose)"
        return 0
    else
        error "❌ $name: ERROR (contenedor no ejecutándose)"
        return 1
    fi
}

# Verificar contenedores Docker
log "🐳 Verificando contenedores Docker..."
check_container "$DB_CONTAINER" "Base de datos"
check_container "$BACKEND_CONTAINER" "Backend"
check_container "$FRONTEND_CONTAINER" "Frontend"

# Verificar endpoints HTTP
log "🌐 Verificando endpoints HTTP..."

# Verificar backend health
if check_http "$BACKEND_URL/health" "Backend Health"; then
    # Verificar endpoints específicos del backend
    check_http "$BACKEND_URL/docs" "Backend API Docs"
    check_http "$BACKEND_URL/api/v1/ocr/supported-formats" "OCR Endpoint"
    check_http "$BACKEND_URL/api/v1/gmail/auth/status" "Gmail API Endpoint"
fi

# Verificar frontend
check_http "$FRONTEND_URL" "Frontend"

# Verificar base de datos
log "🗄️ Verificando base de datos..."
if docker-compose exec -T db pg_isready -U boosting_user -d facturas_boosting > /dev/null 2>&1; then
    success "✅ Base de datos: OK (conexión establecida)"
else
    error "❌ Base de datos: ERROR (no se puede conectar)"
fi

# Verificar espacio en disco
log "💾 Verificando espacio en disco..."
DISK_USAGE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    success "✅ Espacio en disco: OK (${DISK_USAGE}% usado)"
else
    warning "⚠️ Espacio en disco: ADVERTENCIA (${DISK_USAGE}% usado)"
fi

# Verificar memoria
log "🧠 Verificando memoria..."
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ "$MEMORY_USAGE" -lt 80 ]; then
    success "✅ Memoria: OK (${MEMORY_USAGE}% usado)"
else
    warning "⚠️ Memoria: ADVERTENCIA (${MEMORY_USAGE}% usado)"
fi

# Verificar logs de errores
log "📋 Verificando logs de errores..."
ERROR_COUNT=$(docker-compose logs --tail=100 backend 2>/dev/null | grep -i error | wc -l)
if [ "$ERROR_COUNT" -eq 0 ]; then
    success "✅ Logs: OK (sin errores recientes)"
else
    warning "⚠️ Logs: ADVERTENCIA ($ERROR_COUNT errores en los últimos 100 logs)"
fi

# Verificar conectividad de red
log "🌐 Verificando conectividad de red..."
if ping -c 1 8.8.8.8 > /dev/null 2>&1; then
    success "✅ Conectividad: OK (internet accesible)"
else
    warning "⚠️ Conectividad: ADVERTENCIA (sin acceso a internet)"
fi

# Resumen final
log "📊 Resumen del health check:"
echo "=================================="

# Contar servicios OK vs ERROR
TOTAL_CHECKS=0
OK_CHECKS=0

# Verificar cada servicio y contar
if check_http "$BACKEND_URL/health" "Backend" > /dev/null 2>&1; then
    ((OK_CHECKS++))
fi
((TOTAL_CHECKS++))

if check_http "$FRONTEND_URL" "Frontend" > /dev/null 2>&1; then
    ((OK_CHECKS++))
fi
((TOTAL_CHECKS++))

if docker-compose exec -T db pg_isready -U boosting_user -d facturas_boosting > /dev/null 2>&1; then
    ((OK_CHECKS++))
fi
((TOTAL_CHECKS++))

# Mostrar resultado final
if [ "$OK_CHECKS" -eq "$TOTAL_CHECKS" ]; then
    success "🎉 Sistema completamente operativo ($OK_CHECKS/$TOTAL_CHECKS servicios OK)"
    exit 0
elif [ "$OK_CHECKS" -gt 0 ]; then
    warning "⚠️ Sistema parcialmente operativo ($OK_CHECKS/$TOTAL_CHECKS servicios OK)"
    exit 1
else
    error "❌ Sistema no operativo (0/$TOTAL_CHECKS servicios OK)"
    exit 2
fi
