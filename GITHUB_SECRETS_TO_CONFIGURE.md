# GitHub Secrets para Configurar

## 🔐 Secrets que debes agregar en GitHub

Ve a tu repositorio en GitHub: https://github.com/AlejandroPODropi/facturasBst
Luego ve a Settings > Secrets and variables > Actions > New repository secret

### 1. GCP_SA_KEY
**Nombre**: `GCP_SA_KEY`
**Valor**: Copia todo el contenido del archivo `gcp-key.json` que se generó

```bash
# Para ver el contenido del archivo:
cat gcp-key.json
```

### 2. DATABASE_URL
**Nombre**: `DATABASE_URL`
**Valor**: 
```
postgresql://boosting_user:boosting_password@35.232.248.130:5432/facturas_boosting
```

### 3. SECRET_KEY
**Nombre**: `SECRET_KEY`
**Valor**: 
```
Qbkelx9_hIQWDwvG6p9nLNoN4evw4ZHnMP5UKYJE4tM
```

### 4. GMAIL_CLIENT_ID
**Nombre**: `GMAIL_CLIENT_ID`
**Valor**: (Necesitas configurar esto en Google Cloud Console)
```
your-gmail-client-id
```

### 5. GMAIL_CLIENT_SECRET
**Nombre**: `GMAIL_CLIENT_SECRET`
**Valor**: (Necesitas configurar esto en Google Cloud Console)
```
your-gmail-client-secret
```

## 📋 Pasos para Configurar

### Paso 1: Configurar GCP_SA_KEY
1. Ve a GitHub > Settings > Secrets and variables > Actions
2. Haz clic en "New repository secret"
3. Nombre: `GCP_SA_KEY`
4. Valor: Copia todo el contenido de `gcp-key.json`
5. Haz clic en "Add secret"

### Paso 2: Configurar DATABASE_URL
1. Haz clic en "New repository secret"
2. Nombre: `DATABASE_URL`
3. Valor: `postgresql://boosting_user:boosting_password@35.232.248.130:5432/facturas_boosting`
4. Haz clic en "Add secret"

### Paso 3: Configurar SECRET_KEY
1. Haz clic en "New repository secret"
2. Nombre: `SECRET_KEY`
3. Valor: `Qbkelx9_hIQWDwvG6p9nLNoN4evw4ZHnMP5UKYJE4tM`
4. Haz clic en "Add secret"

### Paso 4: Configurar Gmail API (Opcional por ahora)
Si quieres usar la integración Gmail, necesitas:
1. Ir a Google Cloud Console > APIs & Services > Credentials
2. Crear credenciales OAuth 2.0
3. Configurar `GMAIL_CLIENT_ID` y `GMAIL_CLIENT_SECRET`

## 🚀 Activar CI/CD

Una vez configurados los secrets:

### Opción 1: Push a main branch
```bash
git checkout main
git merge deploy-production
git push origin main
```

### Opción 2: Workflow manual
1. Ve a GitHub > Actions
2. Selecciona "🚀 CD - Deploy to GCP"
3. Haz clic en "Run workflow"
4. Selecciona branch y haz clic en "Run workflow"

## ✅ Verificación

Después del despliegue, verifica:
- Backend: https://backend-us-central1-facturasbst.a.run.app/health
- Frontend: https://storage.googleapis.com/facturas-frontend-facturasbst-1759186561/index.html
- API Docs: https://backend-us-central1-facturasbst.a.run.app/docs
