#!/bin/bash

# Script de Verificación para Google Cloud Platform
# Uso: ./scripts/verify-gcp.sh

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
PROJECT_ID="facturasbst"
REGION="us-central1"
BUCKET_NAME="facturas-frontend-$PROJECT_ID"

log "🔍 Verificando despliegue en Google Cloud Platform..."

# Verificar configuración de gcloud
log "⚙️ Verificando configuración de gcloud..."
if gcloud config get-value project | grep -q "$PROJECT_ID"; then
    success "✅ Proyecto configurado: $PROJECT_ID"
else
    error "❌ Proyecto no configurado correctamente"
    exit 1
fi

# Verificar APIs habilitadas
log "🔧 Verificando APIs habilitadas..."
APIS=(
    "cloudbuild.googleapis.com"
    "run.googleapis.com"
    "sqladmin.googleapis.com"
    "storage-api.googleapis.com"
    "artifactregistry.googleapis.com"
)

for api in "${APIS[@]}"; do
    if gcloud services list --enabled --filter="name:$api" --format="value(name)" | grep -q "$api"; then
        success "✅ API habilitada: $api"
    else
        error "❌ API no habilitada: $api"
    fi
done

# Verificar Artifact Registry
log "📦 Verificando Artifact Registry..."
if gcloud artifacts repositories describe facturas-repo --location=$REGION &> /dev/null; then
    success "✅ Artifact Registry: OK"
else
    error "❌ Artifact Registry: ERROR"
fi

# Verificar Cloud SQL
log "🗄️ Verificando Cloud SQL..."
if gcloud sql instances describe facturas-db &> /dev/null; then
    success "✅ Cloud SQL instancia: OK"
    
    # Verificar base de datos
    if gcloud sql databases describe facturas_boosting --instance=facturas-db &> /dev/null; then
        success "✅ Base de datos: OK"
    else
        error "❌ Base de datos: ERROR"
    fi
    
    # Verificar usuario
    if gcloud sql users list --instance=facturas-db --filter="name:boosting_user" --format="value(name)" | grep -q "boosting_user"; then
        success "✅ Usuario de base de datos: OK"
    else
        error "❌ Usuario de base de datos: ERROR"
    fi
else
    error "❌ Cloud SQL instancia: ERROR"
fi

# Verificar Cloud Run
log "🚀 Verificando Cloud Run..."
if gcloud run services describe facturas-backend --region=$REGION &> /dev/null; then
    success "✅ Cloud Run servicio: OK"
    
    # Obtener URL del servicio
    BACKEND_URL=$(gcloud run services describe facturas-backend --region=$REGION --format="value(status.url)")
    log "📍 Backend URL: $BACKEND_URL"
    
    # Verificar que el servicio esté funcionando
    if curl -f -s --max-time 30 "$BACKEND_URL/health" > /dev/null; then
        success "✅ Backend health check: OK"
    else
        error "❌ Backend health check: ERROR"
    fi
    
    # Verificar endpoints específicos
    if curl -f -s --max-time 30 "$BACKEND_URL/api/v1/ocr/supported-formats" > /dev/null; then
        success "✅ OCR endpoint: OK"
    else
        warning "⚠️ OCR endpoint: WARNING"
    fi
    
    if curl -f -s --max-time 30 "$BACKEND_URL/api/v1/gmail/auth/status" > /dev/null; then
        success "✅ Gmail API endpoint: OK"
    else
        warning "⚠️ Gmail API endpoint: WARNING"
    fi
else
    error "❌ Cloud Run servicio: ERROR"
fi

# Verificar Cloud Storage
log "🌐 Verificando Cloud Storage..."
if gsutil ls gs://$BUCKET_NAME &> /dev/null; then
    success "✅ Cloud Storage bucket: OK"
    
    # Verificar que el bucket sea accesible públicamente
    if curl -f -s --max-time 30 "https://storage.googleapis.com/$BUCKET_NAME/" > /dev/null; then
        success "✅ Frontend accesible: OK"
    else
        error "❌ Frontend accesible: ERROR"
    fi
    
    # Verificar archivos en el bucket
    FILE_COUNT=$(gsutil ls gs://$BUCKET_NAME/ | wc -l)
    if [ "$FILE_COUNT" -gt 0 ]; then
        success "✅ Archivos en bucket: $FILE_COUNT archivos"
    else
        error "❌ Archivos en bucket: ERROR (bucket vacío)"
    fi
else
    error "❌ Cloud Storage bucket: ERROR"
fi

# Verificar imágenes Docker
log "🐳 Verificando imágenes Docker..."
BACKEND_IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/facturas-repo/backend:latest"
FRONTEND_IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/facturas-repo/frontend:latest"

if gcloud artifacts docker images list $BACKEND_IMAGE &> /dev/null; then
    success "✅ Imagen backend: OK"
else
    error "❌ Imagen backend: ERROR"
fi

if gcloud artifacts docker images list $FRONTEND_IMAGE &> /dev/null; then
    success "✅ Imagen frontend: OK"
else
    error "❌ Imagen frontend: ERROR"
fi

# Verificar conectividad de red
log "🌐 Verificando conectividad..."
if ping -c 1 8.8.8.8 > /dev/null 2>&1; then
    success "✅ Conectividad internet: OK"
else
    warning "⚠️ Conectividad internet: WARNING"
fi

# Verificar logs recientes
log "📋 Verificando logs recientes..."
ERROR_COUNT=$(gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=facturas-backend" --limit=100 --format="value(textPayload)" | grep -i error | wc -l)
if [ "$ERROR_COUNT" -eq 0 ]; then
    success "✅ Logs recientes: OK (sin errores)"
else
    warning "⚠️ Logs recientes: WARNING ($ERROR_COUNT errores en los últimos 100 logs)"
fi

# Verificar métricas de rendimiento
log "📊 Verificando métricas de rendimiento..."
INSTANCE_COUNT=$(gcloud run services describe facturas-backend --region=$REGION --format="value(status.observedGeneration)")
if [ "$INSTANCE_COUNT" -gt 0 ]; then
    success "✅ Servicio desplegado: OK (generación $INSTANCE_COUNT)"
else
    error "❌ Servicio desplegado: ERROR"
fi

# Resumen final
log "📊 Resumen de verificación:"
echo "=================================="
echo "Proyecto: $PROJECT_ID"
echo "Región: $REGION"
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: https://storage.googleapis.com/$BUCKET_NAME/"
echo "Base de datos: $PROJECT_ID:$REGION:facturas-db"
echo "=================================="

# Contar verificaciones exitosas
TOTAL_CHECKS=0
OK_CHECKS=0

# Contar verificaciones (simplificado)
if gcloud run services describe facturas-backend --region=$REGION &> /dev/null; then
    ((OK_CHECKS++))
fi
((TOTAL_CHECKS++))

if gsutil ls gs://$BUCKET_NAME &> /dev/null; then
    ((OK_CHECKS++))
fi
((TOTAL_CHECKS++))

if gcloud sql instances describe facturas-db &> /dev/null; then
    ((OK_CHECKS++))
fi
((TOTAL_CHECKS++))

# Mostrar resultado final
if [ "$OK_CHECKS" -eq "$TOTAL_CHECKS" ]; then
    success "🎉 Sistema completamente operativo en GCP ($OK_CHECKS/$TOTAL_CHECKS verificaciones OK)"
    exit 0
elif [ "$OK_CHECKS" -gt 0 ]; then
    warning "⚠️ Sistema parcialmente operativo en GCP ($OK_CHECKS/$TOTAL_CHECKS verificaciones OK)"
    exit 1
else
    error "❌ Sistema no operativo en GCP (0/$TOTAL_CHECKS verificaciones OK)"
    exit 2
fi
