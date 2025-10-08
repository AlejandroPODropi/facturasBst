# Solución Completa: Procesamiento en Lote de Facturas

## Resumen del Problema

El sistema de procesamiento en lote de facturas desde Gmail presentaba múltiples errores que impedían la creación exitosa de facturas, especialmente aquellas sin usuario asignado.

## Problemas Identificados y Solucionados

### 1. Error de Validación de `amount` (422 Unprocessable Entity)

**Problema:**
- El esquema Pydantic tenía `gt=0` (greater than 0) para el campo `amount`
- Se enviaba `amount: 0` en las facturas de prueba
- Error: `"Input should be greater than 0"`

**Solución:**
```python
# backend/src/schemas.py
# Antes:
amount: float = Field(..., gt=0, description="Monto de la factura")

# Después:
amount: float = Field(..., ge=0, description="Monto de la factura")
```

**Archivo modificado:** `backend/src/schemas.py` línea 148

### 2. Error de Restricción de Base de Datos para `user_id` (NotNullViolation)

**Problema:**
- La columna `user_id` en la tabla `invoices` tenía restricción `NOT NULL`
- Se necesitaba permitir facturas sin usuario asignado (`user_id: null`)
- Error: `null value in column "user_id" of relation "invoices" violates not-null constraint`

**Solución:**
```sql
-- Aplicación manual de la migración
ALTER TABLE invoices ALTER COLUMN user_id DROP NOT NULL;
```

**Verificación:**
```sql
-- Antes de la migración:
user_id | integer | not null

-- Después de la migración:
user_id | integer | 
```

### 3. Error de Plataforma Docker (Cloud Run)

**Problema:**
- La imagen Docker se construyó para ARM64
- Cloud Run requiere AMD64
- Error: `Container manifest type 'application/vnd.oci.image.index.v1+json' must support amd64/linux`

**Solución:**
```bash
# Reconstrucción con plataforma específica
docker build --platform linux/amd64 -t us-central1-docker.pkg.dev/facturasbst/facturas-repo/backend:latest .
```

## Configuración de Base de Datos

### Conexión Actual
```bash
DATABASE_URL=postgresql://boosting_user:boosting_password_2024@35.232.248.130:5432/facturas_boosting
```

### Usuario y Credenciales
- **Usuario:** `boosting_user`
- **Contraseña:** `boosting_password_2024`
- **Base de datos:** `facturas_boosting`
- **Host:** `35.232.248.130` (IP pública de Cloud SQL)

## Pruebas de Funcionamiento

### 1. Factura sin Usuario (user_id: null)
```bash
curl -X 'POST' \
  'https://backend-493189429371.us-central1.run.app/api/v1/invoices/bulk-create' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "invoices": [
    {
      "email_id": "199b1cb722dd6006",
      "email_subject": "900130916; INVERSIONES SISE GARCIA SCA; FV2255909; 01; INVERSIONES SISE GARCIA SCA;",
      "email_from": "INVERSIONES SISE GARCIA SCA <no-reply@co.edocnube.com>",
      "provider": "INVERSIONES SISE GARCIA SCA",
      "amount": 0,
      "date": "2025-10-05T00:35:24.000Z",
      "description": "Factura FV2255909 emitida por INVERSIONES SISE GARCIA SCA",
      "user_id": null,
      "payment_method": "efectivo",
      "category": "otros",
      "nit": "900130916"
    }
  ],
  "skip_duplicates": true
}'
```

**Resultado:**
```json
{
  "success": true,
  "total_processed": 1,
  "created_count": 1,
  "skipped_count": 0,
  "error_count": 0,
  "created_invoices": [29],
  "skipped_invoices": [],
  "errors": []
}
```

### 2. Factura con Usuario Asignado (user_id: 2)
```bash
curl -X 'POST' \
  'https://backend-493189429371.us-central1.run.app/api/v1/invoices/bulk-create' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "invoices": [
    {
      "email_id": "test123456789",
      "email_subject": "Factura de prueba con usuario",
      "email_from": "test@example.com",
      "provider": "PROVEEDOR DE PRUEBA",
      "amount": 100000,
      "date": "2025-10-05T00:35:24.000Z",
      "description": "Factura de prueba con usuario asignado",
      "user_id": 2,
      "payment_method": "efectivo",
      "category": "otros",
      "nit": "123456789"
    }
  ],
  "skip_duplicates": true
}'
```

**Resultado:**
```json
{
  "success": true,
  "total_processed": 1,
  "created_count": 1,
  "skipped_count": 0,
  "error_count": 0,
  "created_invoices": [30],
  "skipped_invoices": [],
  "errors": []
}
```

## Estado Final del Sistema

### ✅ Funcionalidades Operativas
- **Procesamiento en lote de facturas** desde Gmail
- **Facturas sin usuario** se crean exitosamente con `user_id: null`
- **Facturas con usuario** se crean exitosamente con `user_id` asignado
- **Validación de montos** permite valores >= 0
- **Base de datos** acepta `user_id` nulo
- **Backend desplegado** y funcionando correctamente

### 🔗 URLs del Sistema
- **Backend:** `https://backend-493189429371.us-central1.run.app`
- **Endpoint de procesamiento en lote:** `/api/v1/invoices/bulk-create`

### 📊 Estructura de la Base de Datos
```sql
-- Tabla invoices después de las correcciones
CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),  -- NULL permitido
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    provider VARCHAR(255) NOT NULL,
    amount DOUBLE PRECISION NOT NULL,
    payment_method paymentmethod NOT NULL,
    category expensecategory NOT NULL,
    file_path VARCHAR(500),
    description TEXT,
    status invoicestatus NOT NULL DEFAULT 'PENDING',
    ocr_data JSON,
    ocr_confidence DOUBLE PRECISION,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    nit VARCHAR(20)
);
```

## Archivos Modificados

1. **`backend/src/schemas.py`**
   - Cambio de validación `gt=0` a `ge=0` para el campo `amount`

2. **Base de datos PostgreSQL**
   - Aplicación de migración: `ALTER TABLE invoices ALTER COLUMN user_id DROP NOT NULL;`

3. **Imagen Docker del backend**
   - Reconstrucción con plataforma `linux/amd64`

## Comandos de Despliegue

```bash
# 1. Reconstruir imagen Docker
cd /Users/macairdropi/Codes/facturasBst/backend
docker build --platform linux/amd64 -t us-central1-docker.pkg.dev/facturasbst/facturas-repo/backend:latest .

# 2. Subir imagen al registro
docker push us-central1-docker.pkg.dev/facturasbst/facturas-repo/backend:latest

# 3. Desplegar en Cloud Run
gcloud run deploy backend \
  --image us-central1-docker.pkg.dev/facturasbst/facturas-repo/backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 900 \
  --concurrency 10 \
  --max-instances 10 \
  --set-env-vars="DATABASE_URL=postgresql://boosting_user:boosting_password_2024@35.232.248.130:5432/facturas_boosting"
```

## Conclusión

El sistema de procesamiento en lote de facturas está ahora completamente funcional. Puede manejar tanto facturas con usuario asignado como facturas sin usuario, cumpliendo con los requerimientos del sistema de gestión de facturas desde Gmail.

**Fecha de resolución:** 5 de octubre de 2025
**Estado:** ✅ Resuelto completamente
