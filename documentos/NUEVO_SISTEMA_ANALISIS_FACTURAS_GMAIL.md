# 📧 Sistema de Análisis y Procesamiento en Lote de Facturas desde Gmail

## 🎯 **Objetivo**
Implementar un sistema que consuma el endpoint `/api/v1/gmail/emails/search` para identificar facturas que necesitan ser subidas al sistema, categorizándolas por usuario o marcándolas como "sin usuario".

## 🏗️ **Arquitectura Implementada**

### 1. **Endpoint de Análisis de Facturas**
**URL:** `/api/v1/gmail/analyze-invoices`

**Funcionalidad:**
- Busca correos en Gmail con archivos adjuntos
- Utiliza el `InvoiceEmailProcessor` mejorado para detectar facturas
- Verifica duplicados contra la base de datos existente
- Categoriza facturas por usuario identificado o marca como "sin usuario"

**Parámetros:**
- `query`: Query de búsqueda de Gmail (default: "has:attachment newer_than:30d")
- `max_results`: Número máximo de correos a analizar (default: 50, max: 100)

**Respuesta:**
```json
{
  "success": true,
  "summary": {
    "total_emails_analyzed": 25,
    "invoices_found": 8,
    "invoices_with_user": 3,
    "invoices_without_user": 5,
    "already_uploaded": 2
  },
  "invoices_to_upload": [...],
  "invoices_without_user": [...],
  "already_uploaded": [...],
  "query_used": "has:attachment newer_than:30d",
  "analysis_date": "2025-10-03T02:05:20"
}
```

### 2. **Endpoint de Creación en Lote**
**URL:** `/api/v1/invoices/bulk-create`

**Funcionalidad:**
- Crea múltiples facturas en una sola operación
- Valida existencia de usuarios
- Detecta y omite duplicados
- Maneja errores individuales sin afectar el lote completo

**Esquema de Entrada:**
```json
{
  "invoices": [
    {
      "email_id": "gmail_message_id",
      "email_subject": "Asunto del correo",
      "email_from": "remitente@empresa.com",
      "provider": "Nombre del Proveedor",
      "amount": 150000.0,
      "date": "2025-10-01T00:00:00",
      "description": "Descripción de la factura",
      "user_id": 1,
      "payment_method": "EFECTIVO",
      "category": "SERVICIOS",
      "nit": "1234567890"
    }
  ],
  "skip_duplicates": true
}
```

**Respuesta:**
```json
{
  "success": true,
  "total_processed": 10,
  "created_count": 8,
  "skipped_count": 2,
  "error_count": 0,
  "created_invoices": [1, 2, 3, 4, 5, 6, 7, 8],
  "skipped_invoices": ["email_id_1", "email_id_2"],
  "errors": []
}
```

## 🔧 **Esquemas Pydantic Implementados**

### 1. **BulkInvoiceItem**
```python
class BulkInvoiceItem(BaseModel):
    email_id: str
    email_subject: str
    email_from: str
    provider: str
    amount: float
    date: datetime
    description: Optional[str] = None
    user_id: int
    payment_method: PaymentMethod = PaymentMethod.CASH
    category: ExpenseCategory = ExpenseCategory.OTHER
    nit: Optional[str] = None
```

### 2. **BulkInvoiceCreate**
```python
class BulkInvoiceCreate(BaseModel):
    invoices: List[BulkInvoiceItem]
    skip_duplicates: bool = True
```

### 3. **BulkInvoiceResponse**
```python
class BulkInvoiceResponse(BaseModel):
    success: bool
    total_processed: int
    created_count: int
    skipped_count: int
    error_count: int
    created_invoices: List[int]
    skipped_invoices: List[str]
    errors: List[dict]
```

### 4. **InvoiceAnalysisResult**
```python
class InvoiceAnalysisResult(BaseModel):
    email_id: str
    email_subject: str
    email_from: str
    provider: str
    amount: float
    date: datetime
    description: Optional[str] = None
    attachments: List[dict]
    suggested_user_id: Optional[int] = None
    suggested_user_name: Optional[str] = None
    reason_no_user: Optional[str] = None
```

## 🚀 **Flujo de Trabajo Implementado**

### Paso 1: Análisis de Facturas
```bash
curl -X GET "https://backend-493189429371.us-central1.run.app/api/v1/gmail/analyze-invoices?max_results=50"
```

### Paso 2: Revisión de Resultados
El sistema categoriza automáticamente:
- **invoices_to_upload**: Facturas con usuario identificado
- **invoices_without_user**: Facturas sin usuario (requieren asignación manual)
- **already_uploaded**: Facturas que ya existen en el sistema

### Paso 3: Procesamiento en Lote
```bash
curl -X POST "https://backend-493189429371.us-central1.run.app/api/v1/invoices/bulk-create" \
  -H "Content-Type: application/json" \
  -d '{
    "invoices": [...],
    "skip_duplicates": true
  }'
```

## 🔍 **Características Técnicas**

### 1. **Detección Inteligente de Facturas**
- **4 patrones específicos** para facturación colombiana
- **Palabras clave ampliadas** (bill, billing, cuenta, account)
- **Soporte para archivos ZIP** y binarios
- **Detección de códigos numéricos** y alfanuméricos

### 2. **Extracción de Proveedores**
- **Patrones específicos** para formatos colombianos
- **Limpieza automática** de nombres de empresas
- **Manejo de casos especiales** (S.A.S., S.A., Ltda.)

### 3. **Identificación de Usuarios**
- **Mapeo por dominio** de email del remitente
- **Marcado explícito** de facturas sin usuario
- **Razones detalladas** para facturas sin asignar

### 4. **Manejo de Duplicados**
- **Verificación automática** contra base de datos
- **Comparación por proveedor, monto y fecha**
- **Omisión inteligente** de duplicados

## 📊 **Ejemplo de Uso Completo**

### 1. Analizar facturas disponibles:
```bash
curl -X GET "https://backend-493189429371.us-central1.run.app/api/v1/gmail/analyze-invoices"
```

### 2. Revisar resultados:
```json
{
  "summary": {
    "total_emails_analyzed": 25,
    "invoices_found": 8,
    "invoices_with_user": 3,
    "invoices_without_user": 5,
    "already_uploaded": 2
  }
}
```

### 3. Procesar facturas con usuario:
```bash
curl -X POST "https://backend-493189429371.us-central1.run.app/api/v1/invoices/bulk-create" \
  -H "Content-Type: application/json" \
  -d '{
    "invoices": [
      {
        "email_id": "msg_001",
        "email_subject": "901294241;PAGOS AUTOMATICOS DE COLOMBIA SAS;FVFE255128;01;PAGOS AUTOMATICOS DE COLOMBIA SAS",
        "email_from": "facturacion@pagosautomaticos.com",
        "provider": "Pagos Automaticos De Colombia S.A.S.",
        "amount": 150000.0,
        "date": "2025-10-01T00:00:00",
        "user_id": 1,
        "payment_method": "EFECTIVO",
        "category": "SERVICIOS"
      }
    ],
    "skip_duplicates": true
  }'
```

## 🔐 **Seguridad y Autenticación**

### Requisitos:
- **Autenticación Gmail** requerida para análisis
- **Token persistente** en Google Secret Manager
- **Validación de usuarios** en creación en lote
- **Manejo seguro de errores** sin exposición de datos sensibles

## 📈 **Beneficios del Sistema**

### 1. **Automatización Completa**
- Detección automática de facturas en Gmail
- Procesamiento en lote eficiente
- Reducción de trabajo manual

### 2. **Flexibilidad**
- Categorización automática por usuario
- Manejo de casos sin usuario
- Configuración de parámetros de búsqueda

### 3. **Robustez**
- Manejo de errores individuales
- Detección de duplicados
- Validación completa de datos

### 4. **Trazabilidad**
- Información completa del email origen
- Metadatos de procesamiento
- Logs detallados de operaciones

## 🎯 **Próximos Pasos Sugeridos**

### 1. **Frontend Integration**
- Crear interfaz para análisis de facturas
- Implementar selección masiva de facturas
- Agregar gestión de facturas sin usuario

### 2. **Mejoras de Identificación**
- Implementar mapeo avanzado de dominios a usuarios
- Agregar aprendizaje automático para clasificación
- Crear reglas personalizables de asignación

### 3. **Monitoreo y Reportes**
- Dashboard de análisis de facturas
- Reportes de eficiencia del sistema
- Alertas de facturas sin procesar

## ✅ **Estado Actual**

- ✅ **Backend implementado** y desplegado
- ✅ **Endpoints funcionando** correctamente
- ✅ **Esquemas validados** y probados
- ✅ **Autenticación Gmail** integrada
- ✅ **Almacenamiento persistente** en Secret Manager
- ✅ **Sistema en producción** y operativo

**URLs del Sistema:**
- **Frontend:** https://frontend-493189429371.us-central1.run.app/
- **Backend:** https://backend-493189429371.us-central1.run.app/
- **API Docs:** https://backend-493189429371.us-central1.run.app/docs

---

**¡El sistema está completamente operativo y listo para analizar y procesar facturas desde Gmail de forma automatizada!** 🚀

