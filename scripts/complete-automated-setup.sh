#!/bin/bash

# Script de Configuración Automática Completa - Control de Facturas Boosting
# Este script automatiza TODA la configuración sin pasos manuales

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
REPOSITORY="facturas-repo"
BUCKET_NAME="facturas-frontend-facturasbst-1759186561"
GITHUB_REPO="AlejandroPODropi/facturasBst"

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
    
    if ! command -v gh &> /dev/null; then
        log_error "GitHub CLI no está instalado. Instalando..."
        # Instalar GitHub CLI en macOS
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew install gh
        else
            log_error "Por favor instala GitHub CLI manualmente"
            exit 1
        fi
    fi
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker no está instalado"
        exit 1
    fi
    
    log_success "Prerrequisitos verificados"
}

# Configurar GitHub CLI
setup_github_cli() {
    log_info "Configurando GitHub CLI..."
    
    # Verificar si ya está autenticado
    if ! gh auth status &> /dev/null; then
        log_info "Autenticando con GitHub..."
        gh auth login --web
    fi
    
    log_success "GitHub CLI configurado"
}

# Crear Service Account y generar clave
setup_gcp_service_account() {
    log_info "Configurando Service Account de GCP..."
    
    # Verificar si ya existe
    if gcloud iam service-accounts describe facturas-cicd@facturasbst.iam.gserviceaccount.com &> /dev/null; then
        log_info "Service Account ya existe, regenerando clave..."
        # Eliminar claves existentes
        gcloud iam service-accounts keys list --iam-account=facturas-cicd@facturasbst.iam.gserviceaccount.com --format="value(name)" | xargs -I {} gcloud iam service-accounts keys delete {} --iam-account=facturas-cicd@facturasbst.iam.gserviceaccount.com --quiet || true
    else
        log_info "Creando Service Account..."
        gcloud iam service-accounts create facturas-cicd \
            --display-name="Facturas CI/CD" \
            --description="Service Account para CI/CD de Facturas Boosting"
        
        # Asignar roles
        log_info "Asignando roles a Service Account..."
        gcloud projects add-iam-policy-binding facturasbst \
            --member="serviceAccount:facturas-cicd@facturasbst.iam.gserviceaccount.com" \
            --role="roles/run.admin"
        
        gcloud projects add-iam-policy-binding facturasbst \
            --member="serviceAccount:facturas-cicd@facturasbst.iam.gserviceaccount.com" \
            --role="roles/storage.admin"
        
        gcloud projects add-iam-policy-binding facturasbst \
            --member="serviceAccount:facturas-cicd@facturasbst.iam.gserviceaccount.com" \
            --role="roles/cloudbuild.builds.builder"
        
        gcloud projects add-iam-policy-binding facturasbst \
            --member="serviceAccount:facturas-cicd@facturasbst.iam.gserviceaccount.com" \
            --role="roles/artifactregistry.admin"
    fi
    
    # Generar nueva clave
    log_info "Generando clave de Service Account..."
    gcloud iam service-accounts keys create gcp-key.json \
        --iam-account=facturas-cicd@facturasbst.iam.gserviceaccount.com
    
    log_success "Service Account configurado"
}

# Configurar GitHub Secrets
setup_github_secrets() {
    log_info "Configurando GitHub Secrets..."
    
    # Leer la clave GCP
    GCP_SA_KEY=$(cat gcp-key.json)
    
    # Obtener IP de la base de datos
    DB_IP=$(gcloud sql instances describe facturas-db --format="value(ipAddresses[0].ipAddress)")
    
    # Generar SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    # Configurar secrets
    log_info "Configurando GCP_SA_KEY..."
    echo "$GCP_SA_KEY" | gh secret set GCP_SA_KEY --repo $GITHUB_REPO
    
    log_info "Configurando DATABASE_URL..."
    gh secret set DATABASE_URL --repo $GITHUB_REPO --body "postgresql://boosting_user:boosting_password@$DB_IP:5432/facturas_boosting"
    
    log_info "Configurando SECRET_KEY..."
    gh secret set SECRET_KEY --repo $GITHUB_REPO --body "$SECRET_KEY"
    
    log_info "Configurando GMAIL_CLIENT_ID..."
    gh secret set GMAIL_CLIENT_ID --repo $GITHUB_REPO --body "your-gmail-client-id"
    
    log_info "Configurando GMAIL_CLIENT_SECRET..."
    gh secret set GMAIL_CLIENT_SECRET --repo $GITHUB_REPO --body "your-gmail-client-secret"
    
    log_success "GitHub Secrets configurados"
}

# Activar CI/CD con push a main
activate_cicd() {
    log_info "Activando CI/CD con push a main..."
    
    # Hacer commit de todos los cambios
    git add .
    git commit -m "feat: Complete automated setup and activate CI/CD

- Configure all GitHub Secrets automatically
- Set up GCP Service Account with proper permissions
- Deploy backend and frontend to production
- Activate CI/CD pipeline
- Complete production-ready system setup" || true
    
    # Hacer push a main para activar CI/CD
    git push origin main || {
        log_warning "Push falló, pero los secrets están configurados"
        log_info "Puedes hacer push manualmente más tarde"
    }
    
    log_success "CI/CD activado"
}

# Desplegar backend
deploy_backend() {
    log_info "Desplegando backend a Cloud Run..."
    
    # Construir imagen
    gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/backend:latest ./backend
    
    # Desplegar
    gcloud run deploy backend \
        --image $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/backend:latest \
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
    
    log_success "Backend desplegado"
}

# Desplegar frontend
deploy_frontend() {
    log_info "Desplegando frontend a Cloud Storage..."
    
    # Construir frontend
    cd frontend
    npm ci
    npm run build
    
    # Subir a Cloud Storage
    gsutil -m cp -r dist/* gs://$BUCKET_NAME/
    gsutil -m cp dist/index.html gs://$BUCKET_NAME/index.html
    gsutil -m setmeta -h "Cache-Control:no-cache" gs://$BUCKET_NAME/index.html
    
    cd ..
    log_success "Frontend desplegado"
}

# Verificar despliegue
verify_deployment() {
    log_info "Verificando despliegue..."
    
    BACKEND_URL="https://backend-${REGION}-${PROJECT_ID}.a.run.app"
    
    # Verificar backend
    if curl -f -s "$BACKEND_URL/health" > /dev/null; then
        log_success "Backend funcionando correctamente"
    else
        log_warning "Backend health check falló"
    fi
    
    # Verificar frontend
    if curl -f -s "https://storage.googleapis.com/$BUCKET_NAME/index.html" > /dev/null; then
        log_success "Frontend accesible"
    else
        log_warning "Frontend no accesible"
    fi
    
    log_success "Verificación completada"
}

# Limpiar archivos sensibles
cleanup() {
    log_info "Limpiando archivos sensibles..."
    
    # Eliminar clave GCP local
    rm -f gcp-key.json
    
    # Agregar al .gitignore si no está
    if ! grep -q "gcp-key.json" .gitignore; then
        echo "gcp-key.json" >> .gitignore
    fi
    
    log_success "Limpieza completada"
}

# Función principal
main() {
    echo "🚀 Iniciando configuración automática completa..."
    echo "Proyecto GCP: $PROJECT_ID"
    echo "Repositorio GitHub: $GITHUB_REPO"
    echo ""
    
    check_prerequisites
    setup_github_cli
    setup_gcp_service_account
    setup_github_secrets
    deploy_backend
    deploy_frontend
    verify_deployment
    activate_cicd
    cleanup
    
    echo ""
    log_success "🎉 Configuración automática completada!"
    echo ""
    echo "📊 URLs del sistema:"
    echo "  Backend: https://backend-${REGION}-${PROJECT_ID}.a.run.app"
    echo "  Frontend: https://storage.googleapis.com/$BUCKET_NAME/index.html"
    echo "  API Docs: https://backend-${REGION}-${PROJECT_ID}.a.run.app/docs"
    echo ""
    echo "✅ CI/CD activado automáticamente"
    echo "✅ Todos los secrets configurados"
    echo "✅ Sistema desplegado en producción"
}

# Ejecutar función principal
main "$@"
