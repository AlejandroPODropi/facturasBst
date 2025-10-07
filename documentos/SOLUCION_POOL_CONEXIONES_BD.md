# Solución: Error de Pool de Conexiones Agotado

**Fecha:** 7 de Octubre de 2025  
**Problema:** Errores 500 en el backend con mensajes de CORS aparentes  
**Estado:** ✅ Resuelto y Verificado

---

## 🔍 Síntomas del Problema

### Errores en la Consola del Navegador
```
Access to XMLHttpRequest at 'https://backend-493189429371.us-central1.run.app/api/v1/invoices/' 
from origin 'https://facturas.boostingsas.com' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.

GET https://backend-493189429371.us-central1.run.app/api/v1/invoices/ net::ERR_FAILED 500 (Internal Server Error)
GET https://backend-493189429371.us-central1.run.app/api/v1/users/?skip=0&limit=100 net::ERR_FAILED 500 (Internal Server Error)
```

### Error Real en los Logs del Backend
```
sqlalchemy.exc.TimeoutError: QueuePool limit of size 1 overflow 0 reached, connection timed out, timeout 30.00
```

---

## 🎯 Diagnóstico

### 1. Análisis Inicial - CORS (Falso Positivo)
Inicialmente el error parecía ser de CORS, pero al verificar:
- ✅ Backend tenía CORS configurado correctamente
- ✅ Dominio `facturas.boostingsas.com` en lista permitida
- ✅ Headers CORS presentes en preflight requests (OPTIONS)

### 2. Análisis de Logs - Problema Real
Al revisar los logs de Cloud Run con:
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=backend" --limit=50
```

Se encontró el error real:
```python
sqlalchemy.exc.TimeoutError: QueuePool limit of size 1 overflow 0 reached, 
connection timed out, timeout 30.00 
(Background on this error at: https://sqlalche.me/e/20/3o7r)
```

### 3. Causa Raíz
El pool de conexiones de SQLAlchemy estaba configurado de forma muy restrictiva:

**Archivo:** `backend/src/database.py` (líneas 85-86)
```python
max_overflow=0,     # No permitir conexiones adicionales
pool_size=1         # Solo una conexión en el pool
```

Esto causaba que:
1. Solo 1 conexión disponible en el pool
2. Peticiones simultáneas agotaban el pool
3. Backend retornaba 500 Internal Server Error
4. Sin respuesta HTTP válida, el navegador mostraba error de CORS

---

## 🔧 Solución Implementada

### Cambio en `backend/src/database.py`

**ANTES:**
```python
engine = create_engine(
    direct_url,
    pool_pre_ping=True,
    echo=settings.debug,
    pool_recycle=3600,  # Reciclar conexiones cada hora
    pool_timeout=30,    # Timeout de 30 segundos
    max_overflow=0,     # No permitir conexiones adicionales
    pool_size=1         # Solo una conexión en el pool
)
```

**DESPUÉS:**
```python
engine = create_engine(
    direct_url,
    pool_pre_ping=True,
    echo=settings.debug,
    pool_recycle=3600,  # Reciclar conexiones cada hora
    pool_timeout=30,    # Timeout de 30 segundos
    max_overflow=10,    # Permitir hasta 10 conexiones adicionales
    pool_size=5         # Pool base de 5 conexiones
)
```

### Configuración Resultante
- **Pool base:** 5 conexiones permanentes
- **Overflow:** 10 conexiones adicionales temporales
- **Total máximo:** 15 conexiones simultáneas
- **Timeout:** 30 segundos por conexión
- **Pool recycle:** Conexiones se reciclan cada hora

---

## 🚀 Despliegue

### 1. Build del Backend
```bash
gcloud builds submit --tag us-central1-docker.pkg.dev/facturasbst/facturas-repo/backend:latest ./backend
```

### 2. Deploy en Cloud Run
```bash
gcloud run deploy backend \
  --image=us-central1-docker.pkg.dev/facturasbst/facturas-repo/backend:latest \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated \
  --port=8000 \
  --memory=2Gi \
  --cpu=2 \
  --max-instances=10 \
  --min-instances=0 \
  --timeout=300
```

**Resultado:**
```
Service [backend] revision [backend-00091-2zg] has been deployed and is serving 100 percent of traffic.
Service URL: https://backend-493189429371.us-central1.run.app
```

---

## ✅ Verificación

### 1. Test de Endpoint
```bash
curl -s "https://backend-493189429371.us-central1.run.app/api/v1/users/?skip=0&limit=1"
```

**Resultado:** ✅ Respuesta exitosa con datos JSON

### 2. Test de CORS
```bash
curl -I -H "Origin: https://facturas.boostingsas.com" \
  "https://backend-493189429371.us-central1.run.app/api/v1/users/"
```

**Resultado:** 
```
✅ access-control-allow-origin: https://facturas.boostingsas.com
✅ access-control-allow-credentials: true
```

### 3. Test en Navegador
- ✅ Sin errores en consola
- ✅ Todas las peticiones retornan 200 OK
- ✅ Aplicación completamente funcional

---

## 📊 Comparación: Antes vs Después

### Antes (Con Problema)
| Métrica | Valor |
|---------|-------|
| Pool size | 1 |
| Max overflow | 0 |
| Conexiones totales | 1 |
| Estado | ❌ Timeouts frecuentes |
| Errores | 500 Internal Server Error |

### Después (Resuelto)
| Métrica | Valor |
|---------|-------|
| Pool size | 5 |
| Max overflow | 10 |
| Conexiones totales | 15 |
| Estado | ✅ Sin timeouts |
| Errores | Ninguno |

---

## 🎓 Lecciones Aprendidas

### 1. Los Errores de CORS Pueden ser Engañosos
- Un error 500 del servidor puede manifestarse como error de CORS en el cliente
- Siempre revisar los logs del servidor antes de asumir que es un problema de CORS
- El navegador muestra error de CORS cuando no recibe una respuesta HTTP válida

### 2. Configuración del Pool de Conexiones
- Un pool muy restrictivo causa cuellos de botella
- Para Cloud Run con múltiples instancias:
  - `pool_size`: 5-10 conexiones base
  - `max_overflow`: 10-20 conexiones adicionales
  - `pool_recycle`: 3600s (1 hora) para evitar conexiones obsoletas

### 3. Diagnóstico Sistemático
1. Verificar configuración (CORS, variables, etc.)
2. Revisar logs del servidor
3. Identificar el error raíz
4. Aplicar solución específica al problema real

---

## 🔮 Recomendaciones Futuras

### 1. Monitoreo de Conexiones
Implementar métricas para:
- Número de conexiones activas
- Timeouts de conexión
- Pool exhaustion events

### 2. Ajuste Dinámico
Considerar ajustar el pool según:
- Carga del sistema
- Número de instancias de Cloud Run
- Límites de conexiones de Cloud SQL

### 3. Alertas
Configurar alertas para:
- Errores 500 repetidos
- Timeouts de base de datos
- Pool de conexiones cerca del límite

---

## 📚 Referencias

- [SQLAlchemy Engine Configuration](https://docs.sqlalchemy.org/en/20/core/engines.html)
- [SQLAlchemy Pool Configuration](https://docs.sqlalchemy.org/en/20/core/pooling.html)
- [Google Cloud SQL Best Practices](https://cloud.google.com/sql/docs/mysql/best-practices)

---

## ✅ Resultado Final

**Estado:** ✅ Problema completamente resuelto  
**Fecha de Resolución:** 7 de Octubre de 2025  
**Sistema:** Completamente operativo en https://facturas.boostingsas.com

---

**Notas:**
- El problema era de infraestructura, no de código de aplicación
- La solución fue simple pero el diagnóstico requirió análisis de logs
- El error de CORS era un síntoma secundario, no la causa raíz

