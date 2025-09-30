#!/bin/bash

# Script de Verificación de Despliegue - Control de Facturas Boosting
# Este script verifica que todos los servicios estén funcionando correctamente

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
PROJECT_ID="facturasbst"
REGION="us-central1"
BUCKET_NAME="facturas-frontend-facturasbst-1759186561"

# Funciones de logging
log_info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

# Verificar Cloud Run Backend
verify_backend() {
    log_info "Verificando backend en Cloud Run..."
    
    BACKEND_URL="https://backend-${REGION}-${PROJECT_ID}.a.run.app"
    
    # Verificar que el servicio esté activo
    if gcloud run services describe backend --region=$REGION --format="value(status.conditions[0].status)" | grep -q "True"; then
        log_success "Backend service está activo"
    else
        log_error "Backend service no está activo"
        return 1
    fi
    
    # Verificar health check
    log_info "Verificando health check..."
    if curl -f -s "$BACKEND_URL/health" > /dev/null; then
        log_success "Health check exitoso"
    else
        log_warning "Health check falló"
    fi
    
    # Verificar endpoints principales
    log_info "Verificando endpoints principales..."
    
    # API Documentation
    if curl -f -s "$BACKEND_URL/docs" > /dev/null; then
        log_success "API Documentation accesible"
    else
        log_warning "API Documentation no accesible"
    fi
    
    # Auth endpoint
    if curl -f -s "$BACKEND_URL/auth/login" -X POST -H "Content-Type: application/json" -d '{"username":"test","password":"test"}' > /dev/null 2>&1; then
        log_success "Auth endpoint respondiendo"
    else
        log_warning "Auth endpoint no respondiendo correctamente"
    fi
    
    echo "Backend URL: $BACKEND_URL"
}

# Verificar Cloud Storage Frontend
verify_frontend() {
    log_info "Verificando frontend en Cloud Storage..."
    
    FRONTEND_URL="https://storage.googleapis.com/$BUCKET_NAME/index.html"
    
    # Verificar que el bucket exista
    if gsutil ls gs://$BUCKET_NAME/ > /dev/null 2>&1; then
        log_success "Bucket de frontend existe"
    else
        log_error "Bucket de frontend no existe"
        return 1
    fi
    
    # Verificar archivos principales
    log_info "Verificando archivos del frontend..."
    
    if gsutil ls gs://$BUCKET_NAME/index.html > /dev/null 2>&1; then
        log_success "index.html presente"
    else
        log_error "index.html no encontrado"
    fi
    
    if gsutil ls gs://$BUCKET_NAME/assets/ > /dev/null 2>&1; then
        log_success "Assets presentes"
    else
        log_warning "Assets no encontrados"
    fi
    
    # Verificar accesibilidad web
    if curl -f -s "$FRONTEND_URL" > /dev/null; then
        log_success "Frontend accesible vía web"
    else
        log_warning "Frontend no accesible vía web"
    fi
    
    echo "Frontend URL: $FRONTEND_URL"
}

# Verificar Cloud SQL
verify_database() {
    log_info "Verificando base de datos Cloud SQL..."
    
    # Verificar que la instancia esté activa
    if gcloud sql instances describe facturas-db --format="value(state)" | grep -q "RUNNABLE"; then
        log_success "Instancia de base de datos está activa"
    else
        log_error "Instancia de base de datos no está activa"
        return 1
    fi
    
    # Verificar conexión (requiere IP autorizada)
    log_info "Verificando conexión a la base de datos..."
    if gcloud sql connect facturas-db --user=boosting_user --database=facturas_boosting --quiet < /dev/null 2>&1; then
        log_success "Conexión a base de datos exitosa"
    else
        log_warning "No se pudo verificar conexión a base de datos (puede requerir IP autorizada)"
    fi
}

# Verificar Artifact Registry
verify_artifacts() {
    log_info "Verificando Artifact Registry..."
    
    # Verificar que el repositorio exista
    if gcloud artifacts repositories describe facturas-repo --location=$REGION > /dev/null 2>&1; then
        log_success "Repositorio de artefactos existe"
    else
        log_error "Repositorio de artefactos no existe"
        return 1
    fi
    
    # Verificar imágenes
    log_info "Verificando imágenes Docker..."
    if gcloud artifacts docker images list $REGION-docker.pkg.dev/$PROJECT_ID/facturas-repo/backend > /dev/null 2>&1; then
        log_success "Imágenes Docker presentes"
    else
        log_warning "No se encontraron imágenes Docker"
    fi
}

# Verificar APIs habilitadas
verify_apis() {
    log_info "Verificando APIs habilitadas..."
    
    local apis=(
        "run.googleapis.com"
        "sqladmin.googleapis.com"
        "storage.googleapis.com"
        "cloudbuild.googleapis.com"
        "artifactregistry.googleapis.com"
    )
    
    for api in "${apis[@]}"; do
        if gcloud services list --enabled --filter="name:$api" --format="value(name)" | grep -q "$api"; then
            log_success "API $api habilitada"
        else
            log_warning "API $api no habilitada"
        fi
    done
}

# Generar reporte de estado
generate_report() {
    log_info "Generando reporte de estado..."
    
    echo ""
    echo "📊 REPORTE DE DESPLIEGUE"
    echo "========================="
    echo "Proyecto: $PROJECT_ID"
    echo "Región: $REGION"
    echo "Fecha: $(date)"
    echo ""
    
    echo "🌐 URLs del Sistema:"
    echo "  Backend API: https://backend-${REGION}-${PROJECT_ID}.a.run.app"
    echo "  Frontend: https://storage.googleapis.com/$BUCKET_NAME/index.html"
    echo "  API Docs: https://backend-${REGION}-${PROJECT_ID}.a.run.app/docs"
    echo "  Health Check: https://backend-${REGION}-${PROJECT_ID}.a.run.app/health"
    echo ""
    
    echo "🔧 Servicios GCP:"
    echo "  Cloud Run: backend"
    echo "  Cloud SQL: facturas-db"
    echo "  Cloud Storage: $BUCKET_NAME"
    echo "  Artifact Registry: facturas-repo"
    echo ""
}

# Función principal
main() {
    echo "🔍 Iniciando verificación de despliegue..."
    echo "Proyecto: $PROJECT_ID"
    echo "Región: $REGION"
    echo ""
    
    verify_apis
    verify_artifacts
    verify_database
    verify_backend
    verify_frontend
    generate_report
    
    log_success "Verificación completada! 🎉"
}

# Ejecutar función principal
main "$@"
