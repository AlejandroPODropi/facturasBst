# 🔍 Configuración OCR para Facturas Físicas

Este documento explica cómo configurar y usar la funcionalidad OCR (Reconocimiento Óptico de Caracteres) para procesar facturas físicas en el sistema de Control de Facturas Boosting.

## 📋 Requisitos Previos

### 1. Instalación de Tesseract OCR

#### macOS
```bash
# Usando Homebrew
brew install tesseract
brew install tesseract-lang  # Para soporte de múltiples idiomas

# Verificar instalación
tesseract --version
```

#### Ubuntu/Debian
```bash
# Instalar Tesseract
sudo apt update
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-spa  # Para español
sudo apt install tesseract-ocr-eng  # Para inglés

# Verificar instalación
tesseract --version
```

#### Windows
1. Descargar el instalador desde: https://github.com/UB-Mannheim/tesseract/wiki
2. Instalar con soporte para español e inglés
3. Agregar Tesseract al PATH del sistema

### 2. Dependencias Python

Las dependencias ya están incluidas en `requirements.txt`:

```bash
# Instalar dependencias
pip install pytesseract==0.3.10
pip install PyMuPDF==1.23.8
pip install Pillow==10.1.0
```

## 🚀 Configuración

### 1. Variables de Entorno

No se requieren variables de entorno adicionales para OCR. El servicio OCR se configura automáticamente.

### 2. Configuración de Tesseract

El servicio OCR está configurado para usar:
- **Idiomas**: Español e inglés (`spa+eng`)
- **Modo OCR**: `--oem 3 --psm 6` (mejor para facturas)
- **Formatos soportados**: JPG, JPEG, PNG, TIFF, BMP, PDF

## 📁 Estructura de Archivos

```
backend/src/
├── services/
│   └── ocr_service.py          # Servicio principal de OCR
├── routers/
│   └── ocr.py                  # Endpoints de la API OCR
└── tests/
    └── test_ocr.py             # Tests unitarios
```

## 🔧 Uso de la API

### Endpoints Disponibles

#### 1. Procesar Factura con OCR
```http
POST /api/v1/ocr/process
Content-Type: multipart/form-data

file: [archivo de factura]
user_id: [ID del usuario]
```

**Respuesta:**
```json
{
  "amount": 1500.0,
  "provider": "Supermercado ABC",
  "date": "2024-01-15T00:00:00",
  "invoice_number": "12345",
  "confidence": 0.85,
  "raw_text": "FACTURA\nTotal: $1,500.00...",
  "user_id": 1,
  "user_name": "Juan Pérez"
}
```

#### 2. Procesar y Crear Factura
```http
POST /api/v1/ocr/process-and-create
Content-Type: multipart/form-data

file: [archivo de factura]
user_id: [ID del usuario]
payment_method: [método de pago]
category: [categoría del gasto]
description: [descripción opcional]
```

#### 3. Obtener Formatos Soportados
```http
GET /api/v1/ocr/supported-formats
```

#### 4. Obtener Datos OCR de Factura
```http
GET /api/v1/ocr/invoice/{invoice_id}/ocr-data
```

#### 5. Validar Extracción OCR
```http
POST /api/v1/ocr/validate-extraction
Content-Type: application/json

{
  "amount": 1500.0,
  "provider": "Supermercado ABC",
  "date": "2024-01-15",
  "user_id": 1
}
```

## 🎯 Funcionalidades

### Extracción Automática de Datos

El servicio OCR extrae automáticamente:

1. **Monto**: Detecta valores monetarios en diferentes formatos
2. **Proveedor**: Identifica el nombre del vendedor/empresa
3. **Fecha**: Extrae fechas en múltiples formatos
4. **Número de factura**: Detecta números de comprobante

### Nivel de Confianza

El sistema calcula un nivel de confianza (0.0 - 1.0) basado en:
- **Monto extraído**: 40% del peso
- **Proveedor extraído**: 30% del peso
- **Fecha extraída**: 20% del peso
- **Número de factura**: 10% del peso

### Patrones de Reconocimiento

El servicio utiliza patrones regex optimizados para facturas en español:

```python
# Ejemplos de patrones
amount_patterns = [
    r'total[:\s]*\$?[\s]*([0-9,]+\.?[0-9]*)',
    r'monto[:\s]*\$?[\s]*([0-9,]+\.?[0-9]*)',
    r'importe[:\s]*\$?[\s]*([0-9,]+\.?[0-9]*)',
    # ... más patrones
]
```

## 🧪 Testing

### Ejecutar Tests
```bash
cd backend
pytest tests/test_ocr.py -v
```

### Tests Incluidos

1. **Tests de formato**: Verificar formatos soportados
2. **Tests de extracción**: Probar extracción de datos
3. **Tests de confianza**: Validar cálculo de confianza
4. **Tests de integración**: Probar flujo completo
5. **Tests de error**: Manejo de casos de fallo

## 🎨 Interfaz de Usuario

### Componentes Frontend

1. **OCRProcessor**: Componente principal para procesamiento
2. **OCRProcessing**: Página dedicada para OCR
3. **Integración**: Navegación desde el menú principal

### Flujo de Usuario

1. **Seleccionar usuario**: Elegir colaborador
2. **Subir archivo**: Seleccionar imagen/PDF de factura
3. **Procesar OCR**: Extraer datos automáticamente
4. **Revisar datos**: Validar y editar información extraída
5. **Completar información**: Método de pago y categoría
6. **Crear factura**: Guardar en el sistema

## 🔍 Solución de Problemas

### Problemas Comunes

#### 1. Tesseract no encontrado
```
Error: TesseractNotFoundError
```
**Solución**: Verificar que Tesseract esté instalado y en el PATH

#### 2. Baja precisión de extracción
**Soluciones**:
- Usar imágenes de mayor resolución
- Mejorar la iluminación al fotografiar
- Asegurar que el texto sea legible
- Usar PDFs con texto en lugar de imágenes escaneadas

#### 3. Error de formato no soportado
```
Error: Formato de archivo no soportado
```
**Solución**: Verificar que el archivo sea JPG, PNG, PDF, TIFF o BMP

### Logs y Debugging

El servicio OCR incluye logging detallado:

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

Los logs incluyen:
- Texto extraído por OCR
- Datos procesados
- Nivel de confianza
- Errores de procesamiento

## 📊 Métricas y Monitoreo

### Métricas Disponibles

1. **Tasa de éxito**: Porcentaje de facturas procesadas exitosamente
2. **Nivel de confianza promedio**: Confianza media de extracciones
3. **Tiempo de procesamiento**: Duración del procesamiento OCR
4. **Formatos más usados**: Estadísticas de tipos de archivo

### Monitoreo en Producción

- Configurar alertas para errores de OCR
- Monitorear tiempo de respuesta
- Revisar logs de procesamiento
- Validar calidad de extracciones

## 🔒 Consideraciones de Seguridad

1. **Validación de archivos**: Verificar tipos MIME
2. **Límites de tamaño**: Restringir tamaño de archivos
3. **Limpieza temporal**: Eliminar archivos temporales
4. **Permisos**: Validar acceso a archivos

## 🚀 Próximas Mejoras

1. **Google Vision API**: Integración como alternativa a Tesseract
2. **IA Avanzada**: Clasificación automática de gastos
3. **Procesamiento asíncrono**: Cola de procesamiento con Celery
4. **Mejores patrones**: Optimización de regex para facturas específicas
5. **Validación cruzada**: Comparar con datos históricos

---

**¡La funcionalidad OCR está lista para usar! 🎉**

Para más información, consulta la documentación de la API en `/docs` cuando el servidor esté ejecutándose.
