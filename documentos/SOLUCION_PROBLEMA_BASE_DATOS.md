# Solución del Problema de Conexión a Base de Datos en Producción

## 📋 Resumen Ejecutivo

Este documento describe la resolución completa del problema de conexión a la base de datos PostgreSQL en el entorno de producción de Cloud Run. El problema principal era que el backend no podía conectarse correctamente a Cloud SQL debido a una columna faltante y configuración incorrecta del conector.

## 🔍 Problema Identificado

### Síntomas
- Error 500 en todos los endpoints que requerían acceso a la base de datos
- Mensaje de error: `column "nit" of relation "invoices" does not exist`
- El backend en Cloud Run no podía ejecutar consultas SQL

### Causa Raíz
1. **Columna `nit` faltante**: La columna `nit` existía en la base de datos local pero no en Cloud SQL
2. **Configuración de conexión incorrecta**: El backend no estaba usando el Cloud SQL Connector apropiado

## 🛠️ Solución Implementada

### 1. Configuración del Cloud SQL Connector

**Archivo modificado**: `backend/src/database.py`

```python
# Crear engine de SQLAlchemy
# Usar Cloud SQL connector si está configurado, sino conexión directa
if "host=/cloudsql/" in settings.database_url:
    engine = create_engine(
        "postgresql+pg8000://",
        creator=getconn,
        pool_pre_ping=True,
        echo=settings.debug
    )
else:
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        echo=settings.debug
    )
```

**Cambios realizados**:
- Detección automática del tipo de conexión basada en la URL
- Uso de `pg8000` con Cloud SQL Connector para producción
- Mantenimiento de `psycopg2` para desarrollo local

### 2. Agregado de Columna Faltante

**Comando ejecutado**:
```bash
gcloud sql connect facturas-db --user=boosting_user --database=facturas_boosting
```

**SQL ejecutado**:
```sql
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS nit VARCHAR(20);
CREATE INDEX IF NOT EXISTS idx_invoices_nit ON invoices(nit);
```

### 3. Configuración de Variables de Entorno

**En Cloud Run**:
- `DATABASE_URL`: `postgresql://boosting_user:boosting_password_2024@/facturas_boosting?host=/cloudsql/facturasbst:us-central1:facturas-db`
- Conexión de Cloud SQL: `facturasbst:us-central1:facturas-db`

## 🔧 Pasos de Resolución Detallados

### Paso 1: Diagnóstico del Problema
```bash
# Verificar logs del backend en producción
gcloud run services logs read backend --region=us-central1 --limit=20

# Identificar error específico
# Error: column "nit" of relation "invoices" does not exist
```

### Paso 2: Verificación de Configuración de Base de Datos
```bash
# Verificar instancia de Cloud SQL
gcloud sql instances list

# Verificar bases de datos
gcloud sql databases list --instance=facturas-db

# Verificar usuarios
gcloud sql users list --instance=facturas-db
```

### Paso 3: Configuración del Cloud SQL Connector
```bash
# Instalar dependencia necesaria
pip install pg8000

# Actualizar código para usar Cloud SQL Connector
# Modificar backend/src/database.py
```

### Paso 4: Agregado de Columna Faltante
```bash
# Conectar directamente a Cloud SQL
gcloud sql connect facturas-db --user=boosting_user --database=facturas_boosting

# Ejecutar comandos SQL
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS nit VARCHAR(20);
CREATE INDEX IF NOT EXISTS idx_invoices_nit ON invoices(nit);
```

### Paso 5: Despliegue y Verificación
```bash
# Construir y desplegar backend
gcloud builds submit --tag us-central1-docker.pkg.dev/facturasbst/facturas-repo/backend:latest ./backend

# Desplegar servicio actualizado
gcloud run deploy backend --image us-central1-docker.pkg.dev/facturasbst/facturas-repo/backend:latest --region us-central1 --platform managed --allow-unauthenticated --set-env-vars="DATABASE_URL=postgresql://boosting_user:boosting_password_2024@/facturas_boosting?host=/cloudsql/facturasbst:us-central1:facturas-db" --add-cloudsql-instances=facturasbst:us-central1:facturas-db

# Verificar funcionamiento
curl -f "https://backend-493189429371.us-central1.run.app/api/v1/invoices/?skip=0&limit=5"
```

## 📊 Resultados

### Antes de la Solución
- ❌ Error 500 en todos los endpoints de base de datos
- ❌ Backend no podía conectarse a Cloud SQL
- ❌ Columna `nit` faltante en la tabla `invoices`

### Después de la Solución
- ✅ Endpoint de facturas funcionando correctamente
- ✅ Conexión a Cloud SQL establecida
- ✅ Columna `nit` agregada con índice
- ✅ Respuesta 200 OK con datos de facturas

## 🔍 Verificación de la Solución

### Test de Conectividad
```bash
# Health check
curl -f "https://backend-493189429371.us-central1.run.app/health"
# Respuesta: {"status":"healthy","service":"control-facturas-boosting"}

# Test de endpoint de facturas
curl -f "https://backend-493189429371.us-central1.run.app/api/v1/invoices/?skip=0&limit=5"
# Respuesta: JSON con datos de facturas (200 OK)
```

### Verificación de Base de Datos
```sql
-- Verificar estructura de tabla
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'invoices' 
ORDER BY ordinal_position;

-- Resultado esperado:
-- id, user_id, date, provider, amount, payment_method, category, 
-- file_path, description, status, created_at, updated_at, 
-- ocr_data, ocr_confidence, nit
```

## 📝 Archivos Modificados

1. **`backend/src/database.py`**
   - Agregada lógica de detección automática de tipo de conexión
   - Configuración de Cloud SQL Connector para producción

2. **Base de datos Cloud SQL**
   - Agregada columna `nit VARCHAR(20)` a tabla `invoices`
   - Creado índice `idx_invoices_nit` para optimización

## 🚀 Despliegue

### Comandos de Despliegue
```bash
# Commit de cambios
git add backend/src/database.py
git commit -m "Fix: Corregir conexión a Cloud SQL en producción"
git push origin main

# Construcción y despliegue
gcloud builds submit --tag us-central1-docker.pkg.dev/facturasbst/facturas-repo/backend:latest ./backend
gcloud run deploy backend --image us-central1-docker.pkg.dev/facturasbst/facturas-repo/backend:latest --region us-central1 --platform managed --allow-unauthenticated --set-env-vars="DATABASE_URL=postgresql://boosting_user:boosting_password_2024@/facturas_boosting?host=/cloudsql/facturasbst:us-central1:facturas-db" --add-cloudsql-instances=facturasbst:us-central1:facturas-db
```

## 🔒 Consideraciones de Seguridad

- Las credenciales de base de datos están configuradas como variables de entorno
- La conexión a Cloud SQL usa el Cloud SQL Connector oficial
- Los permisos de base de datos están limitados al usuario `boosting_user`

## 📈 Monitoreo

### Logs a Monitorear
```bash
# Logs del backend
gcloud run services logs read backend --region=us-central1 --limit=50

# Logs de Cloud SQL
gcloud sql operations list --instance=facturas-db
```

### Métricas Clave
- Tiempo de respuesta de endpoints de base de datos
- Tasa de errores 500
- Conexiones activas a la base de datos

## 🛡️ Prevención de Problemas Futuros

1. **Migraciones de Base de Datos**
   - Usar Alembic para todas las modificaciones de esquema
   - Ejecutar migraciones en ambos entornos (local y producción)

2. **Testing**
   - Probar conexiones de base de datos en CI/CD
   - Verificar estructura de base de datos después de despliegues

3. **Monitoreo**
   - Configurar alertas para errores de base de datos
   - Monitorear métricas de conexión

## 📞 Contacto y Soporte

Para problemas relacionados con la base de datos:
- Revisar logs de Cloud Run: `gcloud run services logs read backend --region=us-central1`
- Verificar estado de Cloud SQL: `gcloud sql instances describe facturas-db`
- Consultar este documento para pasos de resolución

---

**Fecha de Resolución**: 30 de Septiembre de 2025  
**Estado**: ✅ Resuelto  
**Versión**: 1.0
