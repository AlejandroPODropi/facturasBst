# ☁️ Despliegue en Google Cloud Platform - Proyecto facturasBst

## 🎯 Configuración Específica para GCP

Esta guía te ayudará a desplegar el Sistema de Control de Facturas Boosting en tu proyecto GCP `facturasBst`.

---

## 🔧 Paso 1: Configurar Google Cloud CLI

### 1.1 Instalar Google Cloud CLI

```bash
# macOS
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Verificar instalación
gcloud version
```

### 1.2 Autenticar y Configurar Proyecto

```bash
# Autenticar con tu cuenta de Google
gcloud auth login

# Configurar proyecto
gcloud config set project facturasBst

# Verificar configuración
gcloud config list
```

---

## 🚀 Paso 2: Habilitar Servicios Necesarios

### 2.1 Habilitar APIs Requeridas

```bash
# Habilitar servicios necesarios
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  sqladmin.googleapis.com \
  storage-api.googleapis.com \
  gmail.googleapis.com

# Verificar servicios habilitados
gcloud services list --enabled
```

### 2.2 Configurar Región

```bash
# Configurar región (recomendado: us-central1)
gcloud config set compute/region us-central1
gcloud config set run/region us-central1
```

---

## 🗄️ Paso 3: Configurar Cloud SQL PostgreSQL

### 3.1 Crear Instancia de Cloud SQL

```bash
# Crear instancia de Cloud SQL
gcloud sql instances create facturas-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --storage-type=SSD \
  --storage-size=10GB \
  --storage-auto-increase \
  --backup \
  --enable-ip-alias

# Verificar instancia
gcloud sql instances describe facturas-db
```

### 3.2 Crear Base de Datos y Usuario

```bash
# Crear base de datos
gcloud sql databases create facturas_boosting --instance=facturas-db

# Crear usuario
gcloud sql users create boosting_user \
  --instance=facturas-db \
  --password=Boosting2024!Secure

# Verificar conexión
gcloud sql connect facturas-db --user=boosting_user --database=facturas_boosting
```

---

## 🐳 Paso 4: Preparar Imágenes Docker

### 4.1 Configurar Docker para GCP

```bash
# Configurar Docker para usar gcloud
gcloud auth configure-docker

# Configurar Artifact Registry
gcloud services enable artifactregistry.googleapis.com

# Crear repositorio
gcloud artifacts repositories create facturas-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="Repositorio para imágenes Docker del sistema de facturas"
```

### 4.2 Construir y Subir Imágenes

```bash
# Construir imagen del backend
cd backend
gcloud builds submit --tag us-central1-docker.pkg.dev/facturasBst/facturas-repo/backend:latest

# Construir imagen del frontend
cd ../frontend
gcloud builds submit --tag us-central1-docker.pkg.dev/facturasBst/facturas-repo/frontend:latest
```

---

## 🚀 Paso 5: Desplegar Backend en Cloud Run

### 5.1 Crear Servicio de Cloud Run

```bash
# Desplegar backend
gcloud run deploy facturas-backend \
  --image=us-central1-docker.pkg.dev/facturasBst/facturas-repo/backend:latest \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated \
  --port=8000 \
  --memory=2Gi \
  --cpu=2 \
  --max-instances=10 \
  --set-env-vars="DATABASE_URL=postgresql://boosting_user:Boosting2024!Secure@/facturas_boosting?host=/cloudsql/facturasBst:us-central1:facturas-db" \
  --add-cloudsql-instances=facturasBst:us-central1:facturas-db

# Verificar despliegue
gcloud run services describe facturas-backend --region=us-central1
```

### 5.2 Obtener URL del Backend

```bash
# Obtener URL del servicio
BACKEND_URL=$(gcloud run services describe facturas-backend --region=us-central1 --format="value(status.url)")
echo "Backend URL: $BACKEND_URL"
```

---

## 🌐 Paso 6: Desplegar Frontend en Cloud Storage

### 6.1 Crear Bucket para Frontend

```bash
# Crear bucket para frontend
gsutil mb gs://facturas-frontend-facturasBst

# Configurar bucket como sitio web
gsutil web set -m index.html -e 404.html gs://facturas-frontend-facturasBst
```

### 6.2 Build y Subir Frontend

```bash
# Build del frontend con URL del backend
cd frontend
echo "VITE_API_URL=$BACKEND_URL" > .env.production
npm run build

# Subir archivos al bucket
gsutil -m cp -r dist/* gs://facturas-frontend-facturasBst

# Configurar permisos públicos
gsutil iam ch allUsers:objectViewer gs://facturas-frontend-facturasBst
```

---

## 🔒 Paso 7: Configurar SSL y Dominio Personalizado

### 7.1 Configurar Load Balancer

```bash
# Crear IP estática
gcloud compute addresses create facturas-ip --global

# Obtener IP
gcloud compute addresses describe facturas-ip --global --format="value(address)"
```

### 7.2 Configurar Certificado SSL

```bash
# Crear certificado SSL
gcloud compute ssl-certificates create facturas-ssl \
  --domains=tu-dominio.com,www.tu-dominio.com \
  --global
```

---

## ⚙️ Paso 8: Configurar Variables de Entorno

### 8.1 Crear Archivo de Configuración

```bash
# Crear archivo de configuración para GCP
cat > .env.gcp << EOF
# Configuración GCP
PROJECT_ID=facturasBst
REGION=us-central1
DATABASE_URL=postgresql://boosting_user:Boosting2024!Secure@/facturas_boosting?host=/cloudsql/facturasBst:us-central1:facturas-db
BACKEND_URL=$BACKEND_URL
FRONTEND_URL=https://tu-dominio.com

# Gmail API (opcional)
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json

# Seguridad
SECRET_KEY=tu-secret-key-muy-largo-y-seguro-para-produccion
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
EOF
```

---

## 🧪 Paso 9: Probar Despliegue

### 9.1 Verificar Backend

```bash
# Probar health check
curl $BACKEND_URL/health

# Probar endpoints
curl $BACKEND_URL/api/v1/ocr/supported-formats
curl $BACKEND_URL/api/v1/gmail/auth/status
```

### 9.2 Verificar Frontend

```bash
# Probar frontend
curl https://storage.googleapis.com/facturas-frontend-facturasBst/index.html
```

---

## 📊 Paso 10: Configurar Monitoreo

### 10.1 Habilitar Cloud Monitoring

```bash
# Habilitar Cloud Monitoring
gcloud services enable monitoring.googleapis.com

# Crear alertas básicas
gcloud alpha monitoring policies create --policy-from-file=monitoring-policy.yaml
```

### 10.2 Configurar Logs

```bash
# Ver logs del backend
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=facturas-backend" --limit=50

# Ver logs de la base de datos
gcloud logging read "resource.type=gce_instance AND resource.labels.instance_id=facturas-db" --limit=50
```

---

## 🔄 Paso 11: Configurar CI/CD

### 11.1 Crear Cloud Build Trigger

```bash
# Crear trigger para GitHub
gcloud builds triggers create github \
  --repo-name=facturasBst \
  --repo-owner=tu-usuario \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml
```

### 11.2 Crear cloudbuild.yaml

```yaml
# cloudbuild.yaml
steps:
  # Build backend
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'us-central1-docker.pkg.dev/$PROJECT_ID/facturas-repo/backend:$COMMIT_SHA', './backend']
  
  # Build frontend
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'us-central1-docker.pkg.dev/$PROJECT_ID/facturas-repo/frontend:$COMMIT_SHA', './frontend']
  
  # Deploy backend
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args: ['run', 'deploy', 'facturas-backend', '--image', 'us-central1-docker.pkg.dev/$PROJECT_ID/facturas-repo/backend:$COMMIT_SHA', '--region', 'us-central1']
  
  # Deploy frontend
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args: ['run', 'deploy', 'facturas-frontend', '--image', 'us-central1-docker.pkg.dev/$PROJECT_ID/facturas-repo/frontend:$COMMIT_SHA', '--region', 'us-central1']
```

---

## 💰 Estimación de Costos GCP

### **Costos Mensuales Estimados**

- **Cloud Run:** $0-50 (dependiendo del tráfico)
- **Cloud SQL (db-f1-micro):** $25-35
- **Cloud Storage:** $5-10
- **Load Balancer:** $18
- **SSL Certificate:** $0 (gratis)
- **Total estimado:** $48-113/mes

### **Optimización de Costos**

```bash
# Configurar auto-scaling
gcloud run services update facturas-backend \
  --region=us-central1 \
  --min-instances=0 \
  --max-instances=5

# Configurar Cloud SQL para apagarse automáticamente
gcloud sql instances patch facturas-db \
  --activation-policy=ON_DEMAND
```

---

## 🆘 Comandos de Gestión

### **Gestión de Servicios**

```bash
# Ver estado de servicios
gcloud run services list --region=us-central1

# Ver logs en tiempo real
gcloud logging tail "resource.type=cloud_run_revision"

# Escalar servicio
gcloud run services update facturas-backend \
  --region=us-central1 \
  --max-instances=20
```

### **Gestión de Base de Datos**

```bash
# Conectar a la base de datos
gcloud sql connect facturas-db --user=boosting_user --database=facturas_boosting

# Crear backup
gcloud sql backups create --instance=facturas-db

# Ver backups
gcloud sql backups list --instance=facturas-db
```

### **Gestión de Storage**

```bash
# Ver archivos en bucket
gsutil ls gs://facturas-frontend-facturasBst

# Actualizar frontend
gsutil -m cp -r dist/* gs://facturas-frontend-facturasBst

# Ver logs de acceso
gsutil logging get gs://facturas-frontend-facturasBst
```

---

## 🎯 Checklist de Despliegue

### ✅ **Pre-Despliegue**
- [ ] Google Cloud CLI instalado y configurado
- [ ] Proyecto `facturasBst` configurado
- [ ] APIs habilitadas
- [ ] Región configurada (us-central1)

### ✅ **Base de Datos**
- [ ] Cloud SQL instancia creada
- [ ] Base de datos `facturas_boosting` creada
- [ ] Usuario `boosting_user` creado
- [ ] Conexión verificada

### ✅ **Backend**
- [ ] Imagen Docker construida
- [ ] Cloud Run servicio desplegado
- [ ] Variables de entorno configuradas
- [ ] Health check funcionando

### ✅ **Frontend**
- [ ] Build de producción creado
- [ ] Bucket de Cloud Storage creado
- [ ] Archivos subidos al bucket
- [ ] Permisos públicos configurados

### ✅ **SSL y Dominio**
- [ ] IP estática creada
- [ ] Certificado SSL creado
- [ ] Load balancer configurado
- [ ] DNS configurado

### ✅ **Monitoreo**
- [ ] Cloud Monitoring habilitado
- [ ] Alertas configuradas
- [ ] Logs configurados
- [ ] CI/CD configurado

---

## 🎉 **¡Despliegue en GCP Completado!**

Con estos pasos, tu Sistema de Control de Facturas Boosting estará funcionando en Google Cloud Platform con:

- ✅ **Backend** en Cloud Run
- ✅ **Base de datos** en Cloud SQL
- ✅ **Frontend** en Cloud Storage
- ✅ **SSL** configurado
- ✅ **Monitoreo** activo
- ✅ **CI/CD** configurado

**¡Tu sistema está listo para producción en GCP! 🚀**
