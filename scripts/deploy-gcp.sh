#!/bin/bash

# Script de Despliegue para Google Cloud Platform
# Uso: ./scripts/deploy-gcp.sh

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
REPOSITORY="facturas-repo"

log "🚀 Iniciando despliegue en Google Cloud Platform..."

# Verificar que gcloud esté instalado
if ! command -v gcloud &> /dev/null; then
    error "Google Cloud CLI no está instalado. Por favor instala gcloud primero."
    exit 1
fi

# Verificar autenticación
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    error "No estás autenticado con Google Cloud. Ejecuta: gcloud auth login"
    exit 1
fi

# Configurar proyecto
log "⚙️ Configurando proyecto: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Habilitar APIs necesarias
log "🔧 Habilitando APIs necesarias..."
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  sqladmin.googleapis.com \
  storage-api.googleapis.com \
  artifactregistry.googleapis.com \
  gmail.googleapis.com

# Configurar región
log "🌍 Configurando región: $REGION"
gcloud config set compute/region $REGION
gcloud config set run/region $REGION

# Crear Artifact Registry si no existe
log "📦 Configurando Artifact Registry..."
if ! gcloud artifacts repositories describe $REPOSITORY --location=$REGION &> /dev/null; then
    gcloud artifacts repositories create $REPOSITORY \
      --repository-format=docker \
      --location=$REGION \
      --description="Repositorio para imágenes Docker del sistema de facturas"
    success "✅ Artifact Registry creado"
else
    log "✅ Artifact Registry ya existe"
fi

# Configurar Docker para Artifact Registry
gcloud auth configure-docker $REGION-docker.pkg.dev

# Crear instancia de Cloud SQL si no existe
log "🗄️ Configurando Cloud SQL..."
if ! gcloud sql instances describe facturas-db &> /dev/null; then
    gcloud sql instances create facturas-db \
      --database-version=POSTGRES_15 \
      --tier=db-f1-micro \
      --region=$REGION \
      --storage-type=SSD \
      --storage-size=10GB \
      --storage-auto-increase \
      --backup
    
    # Crear base de datos
    gcloud sql databases create facturas_boosting --instance=facturas-db
    
    # Crear usuario
    gcloud sql users create boosting_user \
      --instance=facturas-db \
      --password=Boosting2024!Secure
    
    success "✅ Cloud SQL configurado"
else
    log "✅ Cloud SQL ya existe"
fi

# Crear bucket para frontend si no existe
log "🌐 Configurando Cloud Storage..."
BUCKET_NAME="facturas-frontend-$PROJECT_ID"
if ! gsutil ls gs://$BUCKET_NAME &> /dev/null; then
    gsutil mb gs://$BUCKET_NAME
    gsutil web set -m index.html -e 404.html gs://$BUCKET_NAME
    gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME
    success "✅ Cloud Storage configurado"
else
    log "✅ Cloud Storage ya existe"
fi

# Construir y desplegar backend
log "🔨 Construyendo y desplegando backend..."
gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/backend:latest ./backend

# Desplegar en Cloud Run
gcloud run deploy facturas-backend \
  --image=$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/backend:latest \
  --platform=managed \
  --region=$REGION \
  --allow-unauthenticated \
  --port=8000 \
  --memory=2Gi \
  --cpu=2 \
  --max-instances=10 \
  --min-instances=0 \
  --set-env-vars="DATABASE_URL=postgresql://boosting_user:Boosting2024!Secure@/facturas_boosting?host=/cloudsql/$PROJECT_ID:$REGION:facturas-db" \
  --add-cloudsql-instances=$PROJECT_ID:$REGION:facturas-db

# Obtener URL del backend
BACKEND_URL=$(gcloud run services describe facturas-backend --region=$REGION --format="value(status.url)")
success "✅ Backend desplegado: $BACKEND_URL"

# Construir y desplegar frontend
log "🎨 Construyendo y desplegando frontend..."
cd frontend

# Crear archivo de configuración para producción
echo "VITE_API_URL=/api/v1" > .env.production

# Build del frontend
npm ci
npm run build

# Subir al bucket
gsutil -m cp -r dist/* gs://$BUCKET_NAME/
success "✅ Frontend desplegado en: https://storage.googleapis.com/$BUCKET_NAME/"

# Ejecutar migraciones
log "🗄️ Ejecutando migraciones de base de datos..."
cd ../backend
gcloud run services proxy facturas-backend --port=8080 &
PROXY_PID=$!
sleep 10

# Ejecutar migraciones usando el proxy
docker run --rm \
  --network host \
  -e DATABASE_URL="postgresql://boosting_user:Boosting2024!Secure@localhost:5432/facturas_boosting" \
  $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/backend:latest \
  alembic upgrade head

# Detener proxy
kill $PROXY_PID

# Verificar despliegue
log "🏥 Verificando despliegue..."

# Verificar backend
if curl -f -s --max-time 30 "$BACKEND_URL/health" > /dev/null; then
    success "✅ Backend: OK"
else
    error "❌ Backend: ERROR"
fi

# Verificar frontend
if curl -f -s --max-time 30 "https://storage.googleapis.com/$BUCKET_NAME/" > /dev/null; then
    success "✅ Frontend: OK"
else
    error "❌ Frontend: ERROR"
fi

# Mostrar información del despliegue
log "📊 Información del despliegue:"
echo "=================================="
echo "Proyecto: $PROJECT_ID"
echo "Región: $REGION"
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: https://storage.googleapis.com/$BUCKET_NAME/"
echo "Base de datos: $PROJECT_ID:$REGION:facturas-db"
echo "=================================="

success "🎉 ¡Despliegue en GCP completado exitosamente!"

log "🔗 Enlaces útiles:"
echo "- Backend API: $BACKEND_URL"
echo "- Documentación API: $BACKEND_URL/docs"
echo "- Frontend: https://storage.googleapis.com/$BUCKET_NAME/"
echo "- Cloud Console: https://console.cloud.google.com/run?project=$PROJECT_ID"

log "📋 Próximos pasos:"
echo "1. Configurar dominio personalizado (opcional)"
echo "2. Configurar SSL con Load Balancer (opcional)"
echo "3. Configurar monitoreo y alertas"
echo "4. Configurar CI/CD con Cloud Build triggers"
