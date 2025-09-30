# 🔧 Problema: Frontend no puede crear usuarios

## 📋 Diagnóstico

### ✅ Backend funcionando correctamente
- **URL**: https://backend-493189429371.us-central1.run.app/
- **Estado**: ✅ Operativo
- **Creación de usuarios**: ✅ Funcionando (probado con curl)
- **Base de datos**: ✅ Conectada y operativa

### ❌ Frontend con problemas de comunicación
- **URL**: https://frontend-493189429371.us-central1.run.app/
- **Estado**: ⚠️ Accesible pero no puede comunicarse con backend
- **Problema**: Requests a `/api/v1/users/` fallan o timeout

## 🔍 Análisis del Problema

### 1. Configuración de API
El frontend está configurado para usar:
```typescript
const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1'
```

### 2. Configuración de Nginx
Nginx está configurado para hacer proxy de `/api/` al backend:
```nginx
location /api/ {
    proxy_pass https://backend-493189429371.us-central1.run.app;
    # ... headers de proxy
}
```

### 3. Variables de Entorno
- **Configurada**: `VITE_API_URL=https://frontend-493189429371.us-central1.run.app/api/v1`
- **Problema**: El frontend intenta hacer requests a sí mismo, creando un bucle

## 🛠️ Soluciones Intentadas

### ✅ Solución 1: Configurar variable de entorno
```bash
gcloud run services update frontend --region=us-central1 \
  --set-env-vars="VITE_API_URL=https://frontend-493189429371.us-central1.run.app/api/v1"
```
**Resultado**: ❌ Timeout en requests

### ✅ Solución 2: Reconstruir frontend
```bash
cd frontend && gcloud builds submit --tag us-central1-docker.pkg.dev/facturasbst/facturas-repo/frontend:latest
```
**Resultado**: ❌ Build exitoso pero problema persiste

### ✅ Solución 3: Cambiar a URL directa del backend
```bash
gcloud run services update frontend --region=us-central1 \
  --set-env-vars="VITE_API_URL=https://backend-493189429371.us-central1.run.app/api/v1"
```
**Resultado**: ❌ Error de cuota de CPU

## 🚨 Problemas Identificados

### 1. Cuota de CPU Excedida
```
ERROR: Quota exceeded for total allowable CPU per project per region.
```

### 2. Configuración de Proxy
El frontend necesita hacer requests directamente al backend, no a través del proxy de Nginx.

## 💡 Solución Recomendada

### Opción 1: Configurar CORS en el Backend
Permitir que el frontend haga requests directos al backend:

```python
# En backend/src/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend-493189429371.us-central1.run.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Opción 2: Usar URL directa del backend
Configurar el frontend para usar la URL directa del backend:
```bash
VITE_API_URL=https://backend-493189429371.us-central1.run.app/api/v1
```

### Opción 3: Resolver cuota de CPU
- Eliminar revisiones antiguas
- Reducir recursos de servicios
- Solicitar aumento de cuota

## 🎯 Próximos Pasos

1. **Verificar CORS**: Asegurar que el backend permite requests del frontend
2. **Configurar URL directa**: Usar la URL del backend directamente
3. **Resolver cuota**: Liberar recursos o solicitar aumento
4. **Probar comunicación**: Verificar que el frontend puede crear usuarios

## 📊 Estado Actual

- ✅ **Backend**: Completamente funcional
- ✅ **Base de datos**: Conectada y operativa
- ⚠️ **Frontend**: Accesible pero sin comunicación con backend
- ❌ **Creación de usuarios desde frontend**: No funciona

## 🔗 URLs de Referencia

- **Frontend**: https://frontend-493189429371.us-central1.run.app/
- **Backend**: https://backend-493189429371.us-central1.run.app/
- **API Docs**: https://backend-493189429371.us-central1.run.app/docs
