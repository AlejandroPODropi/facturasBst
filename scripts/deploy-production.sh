#!/bin/bash

# Script de Despliegue a Producción - Control de Facturas Boosting
# Este script automatiza el despliegue completo a Google Cloud Platform

set -e  # Exit on any error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
PROJECT_ID="facturasbst"
REGION="us-central1"
REPOSITORY="facturas-repo"
SERVICE_NAME="backend"
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

# Verificar prerrequisitos
check_prerequisites() {
    log_info "Verificando prerrequisitos..."
    
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI no está instalado"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker no está instalado"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        log_error "npm no está instalado"
        exit 1
    fi
    
    log_success "Prerrequisitos verificados"
}

# Configurar proyecto GCP
setup_gcp_project() {
    log_info "Configurando proyecto GCP: $PROJECT_ID"
    
    gcloud config set project $PROJECT_ID
    
    # Habilitar APIs necesarias
    log_info "Habilitando APIs necesarias..."
    gcloud services enable run.googleapis.com
    gcloud services enable sqladmin.googleapis.com
    gcloud services enable storage.googleapis.com
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable artifactregistry.googleapis.com
    gcloud services enable memorystore.googleapis.com
    
    log_success "Proyecto GCP configurado"
}

# Construir y desplegar backend
deploy_backend() {
    log_info "Construyendo y desplegando backend..."
    
    # Construir imagen Docker
    log_info "Construyendo imagen Docker..."
    gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$SERVICE_NAME:latest ./backend
    
    # Desplegar a Cloud Run
    log_info "Desplegando a Cloud Run..."
    gcloud run deploy $SERVICE_NAME \
        --image $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$SERVICE_NAME:latest \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --port 8000 \
        --memory 2Gi \
        --cpu 2 \
        --max-instances 10 \
        --min-instances 0 \
        --timeout 300 \
        --set-env-vars="ENVIRONMENT=production,DEBUG=false"
    
    log_success "Backend desplegado exitosamente"
}

# Construir y desplegar frontend
deploy_frontend() {
    log_info "Construyendo y desplegando frontend..."
    
    # Instalar dependencias y construir
    cd frontend
    log_info "Instalando dependencias de frontend..."
    npm ci
    
    log_info "Construyendo aplicación frontend..."
    npm run build
    
    # Subir a Cloud Storage
    log_info "Subiendo archivos a Cloud Storage..."
    gsutil -m cp -r dist/* gs://$BUCKET_NAME/
    gsutil -m cp dist/index.html gs://$BUCKET_NAME/index.html
    gsutil -m setmeta -h "Cache-Control:no-cache" gs://$BUCKET_NAME/index.html
    
    cd ..
    log_success "Frontend desplegado exitosamente"
}

# Verificar despliegue
verify_deployment() {
    log_info "Verificando despliegue..."
    
    # Obtener URL del backend
    BACKEND_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
    
    # Verificar health check
    log_info "Verificando health check del backend..."
    if curl -f "$BACKEND_URL/health" > /dev/null 2>&1; then
        log_success "Backend está funcionando correctamente"
    else
        log_warning "Backend health check falló, pero el servicio está desplegado"
    fi
    
    # Verificar frontend
    log_info "Verificando frontend..."
    if curl -f "https://storage.googleapis.com/$BUCKET_NAME/index.html" > /dev/null 2>&1; then
        log_success "Frontend está accesible"
    else
        log_warning "Frontend no está accesible"
    fi
    
    # Mostrar URLs
    echo ""
    log_success "🎉 Despliegue completado exitosamente!"
    echo ""
    echo "📊 URLs del sistema:"
    echo "  Backend API: $BACKEND_URL"
    echo "  Frontend: https://storage.googleapis.com/$BUCKET_NAME/index.html"
    echo "  Health Check: $BACKEND_URL/health"
    echo "  API Docs: $BACKEND_URL/docs"
    echo ""
}

# Función principal
main() {
    echo "🚀 Iniciando despliegue a producción..."
    echo "Proyecto: $PROJECT_ID"
    echo "Región: $REGION"
    echo ""
    
    check_prerequisites
    setup_gcp_project
    deploy_backend
    deploy_frontend
    verify_deployment
    
    log_success "Despliegue completado exitosamente! 🎉"
}

# Ejecutar función principal
main "$@"
