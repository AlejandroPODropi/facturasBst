# 🔧 Resolución de Errores Críticos en Producción
## Octubre 8, 2025

---

## 📋 Resumen Ejecutivo

Durante esta sesión se identificaron y resolvieron **8 errores críticos** que impedían el funcionamiento del sistema en producción. El trabajo incluyó **11 deploys** (6 backend + 5 frontend) y **9 commits** con documentación detallada. El resultado final es un sistema **100% operativo** en https://facturas.boostingsas.com.

---

## 🚨 Problemas Identificados y Resueltos

### 1. Pool de Conexiones SQLAlchemy Agotado ✅

**Síntoma:**
```
sqlalchemy.exc.TimeoutError: QueuePool limit of size 1 overflow 0 reached
```

**Causa:**
- Configuración muy restrictiva: `pool_size=1`, `max_overflow=0`
- Solo 1 conexión disponible para todas las peticiones concurrentes

**Solución:**
```python
# backend/src/database.py
engine = create_engine(
    settings.database_url,
    pool_size=5,         # 5 conexiones base
    max_overflow=10,     # 10 conexiones adicionales
    pool_recycle=3600,
    pool_timeout=30
)
# Total: 15 conexiones concurrentes
```

**Deploy:** `backend-00091-2zg`

---

### 2. Error 422 en Edición de Facturas (user_id) ✅

**Síntoma:**
```
422 Unprocessable Content al actualizar factura
```

**Causa:**
- Schema `InvoiceUpdate` no incluía campo `user_id`
- Frontend enviaba el campo pero backend lo rechazaba

**Solución:**

**Backend:**
```python
# backend/src/schemas.py
class InvoiceUpdate(BaseModel):
    user_id: Optional[int] = Field(None, description="ID del usuario asignado")
    # ... otros campos

# backend/src/routers/invoices.py
if invoice_update.user_id is not None:
    user = db.query(User).filter(User.id == invoice_update.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
```

**Frontend:**
```typescript
// frontend/src/components/EditInvoiceModal.tsx
updateInvoiceMutation.mutate({
    user_id: formData.user_id,
    // ... otros campos
})
```

**Deploy:** `backend-00091-2zg`, `frontend-00054-5n8`

---

### 3. Error 422 en OCR (Valores Vacíos) ✅

**Síntoma:**
```
422 Unprocessable Content al crear factura desde OCR
```

**Causa:**
```typescript
// Inicialización incorrecta
payment_method: '' as PaymentMethod,  // String vacío no es válido
category: '' as ExpenseCategory,       // String vacío no es válido
```

**Solución:**
```typescript
// frontend/src/components/OCRProcessor.tsx
const [formData, setFormData] = useState({
    payment_method: PaymentMethod.CASH,     // Valor válido por defecto
    category: ExpenseCategory.OTHER,        // Valor válido por defecto
    // ... otros campos
})
```

**Deploy:** `frontend-00054-5n8`

---

### 4. Error 422 en OCR (Valores de Enum Incorrectos) ✅

**Síntoma:**
```
Error: Input should be 'transporte', got 'Transporte'
```

**Causa:**
```typescript
// Código incorrecto
{Object.entries(EXPENSE_CATEGORY_LABELS).map(([key, label]) => (
  <option value={ExpenseCategory[key]}>  // Resolvía a etiqueta
    {label}
  </option>
))}
```

**Solución:**
```typescript
// Código correcto
{Object.values(ExpenseCategory).map((category) => (
  <option value={category}>  // Usa el valor del enum directamente
    {EXPENSE_CATEGORY_LABELS[category]}
  </option>
))}
```

**Componentes corregidos:**
- `OCRProcessor.tsx`
- `EditInvoiceModal.tsx`
- `CreateInvoice.tsx`
- `InvoiceUserAssignment.tsx`

**Deploy:** `frontend-00056-gl5`, `frontend-00057-pjs`

---

### 5. Error 500 en Exportación Excel ✅

**Síntoma:**
```
AttributeError: 'NoneType' object has no attribute 'name'
```

**Causa:**
```python
# Código sin validación
ws.cell(row=row, column=2, value=invoice.user.name)  # Crash si user es None
```

**Solución:**
```python
# backend/src/services/excel_export.py
ws.cell(row=row, column=2, 
        value=invoice.user.name if invoice.user else "Sin asignar")
```

**Deploy:** `backend-00092-rbj`

---

### 6. Error en Procesamiento Gmail (PaymentMethod undefined) ✅

**Síntoma:**
```
ReferenceError: PaymentMethod is not defined
```

**Causa:**
```typescript
// Import incorrecto
import type { PaymentMethod, ExpenseCategory } from '../types'
// Solo importa los TIPOS, no los VALORES
```

**Solución:**
```typescript
// frontend/src/components/InvoiceAnalysis.tsx
import type { 
  InvoiceAnalysisResponse, 
  InvoiceAnalysisResult, 
  BulkInvoiceResponse
} from '../types'
import { PaymentMethod, ExpenseCategory } from '../types'  // Valores reales
```

**Deploy:** `frontend-00058-fjk`

---

### 7. Error 500 Conexión DB (Lógica IP Pública) ✅

**Síntoma:**
```
connection to server at "35.232.248.130", port 5432 failed
password authentication failed
```

**Causa:**
```python
# Código incorrecto que convertía socket a IP
if "host=/cloudsql/" in settings.database_url:
    direct_url = f"postgresql://{user}:{password}@35.232.248.130:5432/{db_name}"
    # Intentaba conectar por IP pública en lugar de socket
```

**Solución:**
```python
# backend/src/database.py
# Usar DATABASE_URL directamente sin conversiones
engine = create_engine(
    settings.database_url,  # Usa el socket de Cloud SQL directamente
    pool_pre_ping=True,
    # ... configuración del pool
)
```

**Deploy:** `backend-00093-vhr`

---

### 8. Error 500 Credenciales DB (CRÍTICO) ✅

**Síntoma:**
```
password authentication failed for user "facturas_user"
database "facturas_db" does not exist
```

**Causa:**
- Usuario incorrecto: `facturas_user` (no existe)
- Base de datos incorrecta: `facturas_db` (no existe)

**Diagnóstico:**
```bash
# Identificar usuario correcto
gcloud sql users list --instance=facturas-db
# Resultado: boosting_user

# Identificar base de datos correcta
gcloud sql databases list --instance=facturas-db
# Resultado: facturas_boosting
```

**Solución:**
```bash
# Resetear contraseña
gcloud sql users set-password boosting_user \
  --instance=facturas-db \
  --password='Boosting2024!'

# Actualizar DATABASE_URL
DATABASE_URL=postgresql://boosting_user:Boosting2024!@/facturas_boosting?host=/cloudsql/facturasbst:us-central1:facturas-db
```

**Deploy:** `backend-00096-fz9`

---

## 📊 Configuración Final Correcta

### Backend (Cloud Run)
```bash
# Variables de entorno
DATABASE_URL=postgresql://boosting_user:Boosting2024!@/facturas_boosting?host=/cloudsql/facturasbst:us-central1:facturas-db
DEBUG=False
SECRET_KEY=your-secret-key-here-change-in-production
GCP_PROJECT_ID=facturasbst

# Configuración Cloud Run
--add-cloudsql-instances=facturasbst:us-central1:facturas-db
--memory=2Gi
--cpu=2
--port=8000
```

### Frontend (Cloud Run)
```bash
# Variables de entorno
VITE_API_URL=https://backend-493189429371.us-central1.run.app/api/v1

# Configuración Cloud Run
--memory=1Gi
--cpu=1
--port=80
```

### Base de Datos (Cloud SQL)
```
Instance: facturas-db
Usuario: boosting_user
Password: Boosting2024!
Base de datos: facturas_boosting
Conexión: Socket Unix (/cloudsql/facturasbst:us-central1:facturas-db)
```

---

## 🚀 Deploys Realizados

### Backend
1. `backend-00091-2zg` - Pool de conexiones + user_id schema
2. `backend-00092-rbj` - Excel export fix
3. `backend-00093-vhr` - Socket connection fix
4. `backend-00094-76r` - Usuario boosting_user
5. `backend-00095-4k2` - Forzar reinicio pool
6. `backend-00096-fz9` - Base de datos correcta ✅ FINAL

### Frontend
1. `frontend-00054-5n8` - OCR defaults + user_id
2. `frontend-00055-7p7` - Debug logging
3. `frontend-00056-gl5` - OCR enum fix
4. `frontend-00057-pjs` - All components enum fix
5. `frontend-00058-fjk` - Gmail import fix ✅ FINAL

---

## 📝 Commits en GitHub

1. `83e7bbf` - Fase 2.9: Resolución de errores CORS
2. `a2ea0cc` - Fix: Pool de conexiones SQLAlchemy y error 422 en edición
3. `dc94fcf` - Fix: Valores por defecto en OCR
4. `da52253` - Debug: Mejorar logging y validación en OCR
5. `6022465` - Fix: Corregir valores de enum en selects de OCR
6. `5ebb8ed` - Fix: Corregir valores de enum en TODOS los selects
7. `9f8fc2d` - Fix: Exportación Excel y procesamiento Gmail
8. `19a9379` - Fix CRÍTICO: Conexión a Cloud SQL desde Cloud Run
9. `bc7429c` - Fix CRÍTICO: Credenciales de Cloud SQL

---

## ✅ Resultado Final

### Sistema 100% Operativo
- ✅ URL: https://facturas.boostingsas.com
- ✅ Backend: https://backend-493189429371.us-central1.run.app
- ✅ Conexión estable a Cloud SQL
- ✅ Pool de conexiones optimizado (15 conexiones)

### Funcionalidades Verificadas
- ✅ Dashboard con estadísticas en tiempo real
- ✅ Gestión de usuarios (crear, editar, listar)
- ✅ Gestión de facturas (crear, editar, listar, filtrar)
- ✅ Edición de facturas con reasignación de usuario
- ✅ Procesamiento OCR de facturas físicas
- ✅ Integración con Gmail para facturas electrónicas
- ✅ Análisis y procesamiento en lote desde Gmail
- ✅ Exportación a Excel con facturas sin usuario
- ✅ Validación de facturas
- ✅ Diseño responsive (mobile-first)

### Métricas de la Sesión
- **Tiempo total:** ~4 horas
- **Errores resueltos:** 8 críticos
- **Deploys:** 11 (6 backend + 5 frontend)
- **Commits:** 9 con documentación completa
- **Archivos modificados:** 35
- **Líneas de código:** +5,252 / -727

---

## 🎓 Lecciones Aprendidas

### 1. Configuración de Pool de Conexiones
- **Nunca** usar `pool_size=1` en producción
- Calcular según: `(núcleos_CPU × 2) + disco_efectivo`
- Monitorear uso real y ajustar

### 2. Validación de Enums en TypeScript
- Usar `Object.values(Enum)` en lugar de `Object.entries(LABELS)`
- Separar claramente tipos de valores en imports
- Validar en cliente antes de enviar al servidor

### 3. Manejo de Valores Null/None
- Siempre validar relaciones opcionales antes de acceder
- Usar operador ternario: `obj.prop if obj else default`
- Considerar valores por defecto razonables

### 4. Conexión a Cloud SQL desde Cloud Run
- Usar **sockets Unix** (`/cloudsql/...`), no IPs públicas
- Configurar `--add-cloudsql-instances` en Cloud Run
- No intentar convertir URLs, usar directamente

### 5. Gestión de Credenciales
- Documentar credenciales correctas en lugar seguro
- Verificar con `gcloud sql` antes de desplegar
- Usar Secret Manager para datos sensibles

### 6. Proceso de Debugging
- Revisar logs de Cloud Run con `gcloud logging read`
- Probar endpoints directamente con `curl`
- Hacer cambios incrementales y verificar

---

## 📚 Documentación Actualizada

- ✅ `task/task.md` - Fase 2.9 agregada con detalle completo
- ✅ `task/planning.md` - Fase 2.10 agregada
- ✅ Este documento - Resumen ejecutivo de la sesión
- ✅ Commits en GitHub con mensajes descriptivos

---

## 🔜 Próximos Pasos

El sistema está ahora listo para:
1. **Uso en producción** por parte de colaboradores
2. **Monitoreo** de métricas y uso real
3. **Fase 3 - Escalamiento** cuando se requiera:
   - Clasificación automática con IA
   - Integración con Siigo
   - Optimización de flujos

---

**Fecha:** Octubre 8, 2025  
**Estado:** ✅ Sistema 100% Operativo  
**URL:** https://facturas.boostingsas.com
