# Configuración de GitHub Secrets para CI/CD

Este documento explica cómo configurar los secrets necesarios en GitHub para el despliegue automático a GCP.

## 🔐 Secrets Requeridos

### 1. GCP_SA_KEY
**Descripción**: Clave de la Service Account de Google Cloud Platform
**Tipo**: JSON completo del archivo de credenciales

**Cómo obtenerlo**:
```bash
# Crear Service Account (si no existe)
gcloud iam service-accounts create facturas-cicd \
    --display-name="Facturas CI/CD" \
    --description="Service Account para CI/CD de Facturas Boosting"

# Asignar roles necesarios
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

# Crear y descargar clave
gcloud iam service-accounts keys create gcp-key.json \
    --iam-account=facturas-cicd@facturasbst.iam.gserviceaccount.com
```

**Valor**: Contenido completo del archivo `gcp-key.json`

### 2. DATABASE_URL
**Descripción**: URL de conexión a la base de datos PostgreSQL en Cloud SQL
**Valor**: `postgresql://boosting_user:boosting_password@35.232.248.130:5432/facturas_boosting`

### 3. SECRET_KEY
**Descripción**: Clave secreta para JWT tokens
**Valor**: Una cadena aleatoria segura (mínimo 32 caracteres)

**Generar clave**:
```python
import secrets
print(secrets.token_urlsafe(32))
```

### 4. GMAIL_CLIENT_ID
**Descripción**: Client ID de la aplicación Gmail API
**Valor**: Obtener de Google Cloud Console > APIs & Services > Credentials

### 5. GMAIL_CLIENT_SECRET
**Descripción**: Client Secret de la aplicación Gmail API
**Valor**: Obtener de Google Cloud Console > APIs & Services > Credentials

## 📋 Pasos para Configurar

### 1. Ir a GitHub Repository Settings
1. Navegar a tu repositorio en GitHub
2. Hacer clic en "Settings"
3. En el menú lateral, hacer clic en "Secrets and variables" > "Actions"

### 2. Agregar cada Secret
1. Hacer clic en "New repository secret"
2. Ingresar el nombre del secret (ej: `GCP_SA_KEY`)
3. Ingresar el valor del secret
4. Hacer clic en "Add secret"

### 3. Verificar Secrets Configurados
Los siguientes secrets deben estar configurados:
- ✅ `GCP_SA_KEY`
- ✅ `DATABASE_URL`
- ✅ `SECRET_KEY`
- ✅ `GMAIL_CLIENT_ID`
- ✅ `GMAIL_CLIENT_SECRET`

## 🔧 Configuración Adicional

### Actualizar Token de GitHub
Para que GitHub Actions funcione correctamente, necesitas un Personal Access Token con scope `workflow`:

1. Ir a GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)
2. Hacer clic en "Generate new token (classic)"
3. Seleccionar los siguientes scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
   - ✅ `write:packages` (Upload packages to GitHub Package Registry)
4. Generar y copiar el token
5. Actualizar tu configuración local de Git:
```bash
git remote set-url origin https://YOUR_TOKEN@github.com/AlejandroPODropi/facturasBst.git
```

## 🚀 Activar CI/CD

Una vez configurados todos los secrets:

1. **Hacer push a main branch**:
```bash
git checkout main
git merge deploy-production
git push origin main
```

2. **O usar workflow_dispatch**:
   - Ir a Actions tab en GitHub
   - Seleccionar "🚀 CD - Deploy to GCP"
   - Hacer clic en "Run workflow"
   - Seleccionar branch y hacer clic en "Run workflow"

## 🔍 Verificar Despliegue

Después del despliegue, verificar:

1. **Backend Health Check**:
```bash
curl https://backend-us-central1-facturasbst.a.run.app/health
```

2. **Frontend**:
```bash
curl https://storage.googleapis.com/facturas-frontend-facturasbst-1759186561/index.html
```

3. **API Documentation**:
```bash
curl https://backend-us-central1-facturasbst.a.run.app/docs
```

## 🛠️ Troubleshooting

### Error: "Permission denied"
- Verificar que la Service Account tenga los roles correctos
- Verificar que el archivo `gcp-key.json` sea válido

### Error: "Secret not found"
- Verificar que todos los secrets estén configurados en GitHub
- Verificar que los nombres de los secrets coincidan exactamente

### Error: "Workflow scope required"
- Actualizar el Personal Access Token con scope `workflow`
- Reconfigurar la URL remota de Git

## 📞 Soporte

Si encuentras problemas:
1. Revisar los logs en GitHub Actions
2. Verificar la configuración de GCP
3. Consultar la documentación de troubleshooting
