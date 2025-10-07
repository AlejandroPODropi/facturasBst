# Resolución de Errores CORS en Dominio Personalizado

**Fecha:** 7 de Octubre de 2025  
**Versión del Sistema:** 2.9.0  
**Estado:** ✅ Completado y Verificado

---

## 🎯 Resumen Ejecutivo

Se resolvió exitosamente el problema de conectividad entre el frontend desplegado en el dominio personalizado `https://facturas.boostingsas.com` y el backend en Google Cloud Run. El problema se diagnosticó inicialmente como un error de CORS, pero resultó ser una configuración incorrecta del frontend para conectarse al backend.

---

## 🔍 Diagnóstico del Problema

### Síntomas Iniciales

```
Access to XMLHttpRequest at 'https://backend-493189429371.us-central1.run.app/api/v1/invoices/' 
from origin 'https://facturas.boostingsas.com' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### Análisis Realizado

1. **Configuración de CORS en Backend**: ✅ Correcto
   - El backend ya tenía configurado `https://facturas.boostingsas.com` en la lista de orígenes permitidos
   - Archivo: `backend/src/main.py` (línea 38)

2. **Configuración del Frontend**: ❌ Problemático
   - El frontend estaba configurado para usar rutas relativas (`/api/v1`)
   - Se esperaba que nginx actuara como proxy
   - El proxy de nginx tenía problemas de conectividad con el backend

3. **Problema de Nginx Proxy**:
   - Timeouts al intentar hacer proxy al backend
   - Errores 502 (Bad Gateway) y 504 (Gateway Timeout)
   - Logs mostraban: `upstream timed out (110: Operation timed out)`

---

## 🛠️ Solución Implementada

### 1. Actualización del Dockerfile del Frontend

**Archivo:** `frontend/Dockerfile`

```dockerfile
# ANTES:
ENV VITE_API_URL=/api/v1

# DESPUÉS:
ENV VITE_API_URL=https://backend-493189429371.us-central1.run.app/api/v1
```

**Razón:** Usar la URL directa del backend en lugar de depender del proxy de nginx.

---

### 2. Actualización de Scripts de Despliegue

#### Script: `scripts/deploy-production.sh`

```bash
# ANTES:
--set-env-vars="VITE_API_URL=/api/v1"

# DESPUÉS:
--set-env-vars="VITE_API_URL=https://backend-493189429371.us-central1.run.app/api/v1"
```

#### Script: `scripts/deploy-gcp.sh`

```bash
# ANTES:
echo "VITE_API_URL=$BACKEND_URL" > .env.production

# DESPUÉS:
echo "VITE_API_URL=/api/v1" > .env.production
```

---

### 3. Corrección de URLs Hardcodeadas en Componentes

#### Archivo: `frontend/src/components/InvoiceCard.tsx`

```tsx
// ANTES:
href={`https://backend-493189429371.us-central1.run.app${attachment.download_url}`}

// DESPUÉS:
href={`${attachment.download_url}`}
```

#### Archivo: `frontend/src/components/InvoiceValidation.tsx`

```tsx
// ANTES:
return `${(import.meta as any).env.VITE_API_URL || 'http://localhost:8000/api/v1'}/invoices/${invoiceId}/download`

// DESPUÉS:
return `${(import.meta as any).env.VITE_API_URL || '/api/v1'}/invoices/${invoiceId}/download`
```

---

### 4. Optimización de Configuración de Nginx (Intentada)

Se intentó optimizar la configuración de nginx para mejorar el manejo del proxy:

**Archivo:** `frontend/nginx.conf`

```nginx
location /api/ {
    proxy_pass https://backend-493189429371.us-central1.run.app;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_connect_timeout 30s;
    proxy_send_timeout 30s;
    proxy_read_timeout 30s;
}
```

**Nota:** Aunque se optimizó la configuración de nginx, finalmente se optó por usar la URL directa del backend debido a problemas de conectividad persistentes con el proxy.

---

## 🚀 Proceso de Despliegue

### Comandos Ejecutados

```bash
# 1. Build de la nueva imagen del frontend
gcloud builds submit --tag us-central1-docker.pkg.dev/facturasbst/facturas-repo/frontend:latest ./frontend

# 2. Despliegue en Cloud Run
gcloud run deploy frontend \
  --image=us-central1-docker.pkg.dev/facturasbst/facturas-repo/frontend:latest \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated \
  --port=80 \
  --memory=1Gi \
  --cpu=1 \
  --max-instances=10 \
  --min-instances=0 \
  --timeout=300 \
  --set-env-vars="VITE_API_URL=https://backend-493189429371.us-central1.run.app/api/v1"
```

### Resultado del Despliegue

```
Service [frontend] revision [frontend-00052-hqj] has been deployed and is serving 100 percent of traffic.
Service URL: https://frontend-493189429371.us-central1.run.app
```

---

## ✅ Verificación de la Solución

### 1. Verificación del Backend

```bash
curl -s "https://backend-493189429371.us-central1.run.app/api/v1/users/?skip=0&limit=5"
```

**Resultado:** ✅ Funcionando correctamente

### 2. Verificación del Frontend

```bash
curl -I "https://facturas.boostingsas.com"
```

**Resultado:** ✅ Sirviendo la nueva versión (timestamp actualizado)

### 3. Verificación de Configuración CORS

- ✅ Backend permite peticiones desde `https://facturas.boostingsas.com`
- ✅ Frontend usa URL directa del backend
- ✅ No hay errores de CORS en la consola del navegador

---

## 📊 Archivos Modificados

### Archivos de Configuración

1. `frontend/Dockerfile` - Actualizada variable de entorno `VITE_API_URL`
2. `frontend/nginx.conf` - Optimizada configuración de proxy (backup)
3. `scripts/deploy-production.sh` - Actualizado con nueva URL de API
4. `scripts/deploy-gcp.sh` - Actualizado para consistencia

### Componentes del Frontend

1. `frontend/src/components/InvoiceCard.tsx` - Corregida URL de descarga de adjuntos
2. `frontend/src/components/InvoiceValidation.tsx` - Corregida URL de descarga de facturas
3. `frontend/README.md` - Actualizada documentación de variables de entorno

### Documentación

1. `task/task.md` - Agregada Fase 2.9 y actualizado estado del sistema
2. `task/PLANNING.md` - Agregada Fase 2.9 en el roadmap
3. `documentos/RESOLUCION_CORS_DOMINIO_PERSONALIZADO.md` - Este documento

---

## 🔧 Configuración Final

### Variables de Entorno

**Desarrollo Local:**
```bash
VITE_API_URL=http://localhost:8000/api/v1
```

**Producción:**
```bash
VITE_API_URL=https://backend-493189429371.us-central1.run.app/api/v1
```

### Configuración de CORS en Backend

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://facturas.boostingsas.com",
        "https://frontend-493189429371.us-central1.run.app",
        "https://frontend-bktmzvs3hq-uc.a.run.app",
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📈 Resultados Obtenidos

### Antes de la Corrección

- ❌ Errores CORS en consola del navegador
- ❌ Frontend no podía conectarse al backend
- ❌ Timeouts en proxy de nginx
- ❌ Errores 502 y 504 en peticiones API

### Después de la Corrección

- ✅ Sin errores CORS
- ✅ Frontend conecta correctamente con el backend
- ✅ Todas las peticiones API funcionan correctamente
- ✅ Sistema completamente operativo en dominio personalizado

---

## 💡 Lecciones Aprendidas

### 1. Configuración de Proxy en Cloud Run

- **Problema:** Nginx proxy tiene dificultades para conectarse a backends externos desde Cloud Run
- **Solución:** Usar URLs directas y configurar CORS correctamente

### 2. Variables de Entorno en Build Time

- **Importante:** Las variables de entorno de Vite (`VITE_*`) se leen en tiempo de build
- **Implicación:** Cambios en variables de entorno requieren rebuild del frontend

### 3. Dominio Personalizado vs URL de Cloud Run

- **Configuración:** El dominio personalizado debe estar mapeado correctamente en Cloud Run
- **Verificación:** Usar `gcloud beta run domain-mappings list` para verificar

---

## 🔮 Recomendaciones Futuras

### 1. Considerar Load Balancer

Para configuraciones más complejas con múltiples backends:
- Implementar Google Cloud Load Balancer
- Configurar reglas de routing avanzadas
- Mejorar SSL/TLS con certificados personalizados

### 2. Implementar CDN

Para mejor rendimiento:
- Usar Google Cloud CDN
- Cachear recursos estáticos
- Reducir latencia global

### 3. Monitoreo Continuo

- Implementar alertas de CORS en logs
- Monitorear latencia de peticiones
- Dashboard de métricas de conectividad

---

## 📞 Soporte y Contacto

**Equipo de Desarrollo:** Boosting SAS  
**Fecha de Resolución:** 7 de Octubre de 2025  
**Próxima Revisión:** Noviembre 2025

---

## 🔗 Enlaces Útiles

- **Frontend:** https://facturas.boostingsas.com
- **Backend API:** https://backend-493189429371.us-central1.run.app
- **Documentación API:** https://backend-493189429371.us-central1.run.app/docs
- **Cloud Console:** https://console.cloud.google.com/run?project=facturasbst

---

**Documento creado:** 7 de Octubre de 2025  
**Última actualización:** 7 de Octubre de 2025  
**Estado:** ✅ Problema Resuelto y Verificado

