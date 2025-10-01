# 🔍 Configuración Detallada de OCR

## 🎯 Objetivo

Esta guía te ayudará a configurar completamente la funcionalidad OCR (Reconocimiento Óptico de Caracteres) para procesar facturas físicas automáticamente.

---

## 🔧 Requisitos Previos

1. **Tesseract OCR** instalado en el sistema
2. **Python 3.8+** con las dependencias necesarias
3. **Archivos de imagen o PDF** de facturas para procesar

---

## 📦 Instalación de Tesseract OCR

### macOS

```bash
# Usando Homebrew (recomendado)
brew install tesseract
brew install tesseract-lang  # Para soporte de múltiples idiomas

# Verificar instalación
tesseract --version
```

### Ubuntu/Debian

```bash
# Actualizar repositorios
sudo apt update

# Instalar Tesseract
sudo apt install tesseract-ocr

# Instalar paquetes de idiomas
sudo apt install tesseract-ocr-spa  # Para español
sudo apt install tesseract-ocr-eng  # Para inglés
sudo apt install tesseract-ocr-fra  # Para francés (opcional)

# Verificar instalación
tesseract --version
```

### Windows

1. **Descargar el instalador:**
   - Ve a: https://github.com/UB-Mannheim/tesseract/wiki
   - Descarga la versión más reciente para Windows

2. **Instalar:**
   - Ejecuta el instalador como administrador
   - Selecciona "Additional language data" durante la instalación
   - Asegúrate de incluir español e inglés

3. **Configurar PATH:**
   - Agrega la ruta de instalación al PATH del sistema
   - Ejemplo: `C:\Program Files\Tesseract-OCR`

4. **Verificar instalación:**
   ```cmd
   tesseract --version
   ```

---

## 🐍 Instalación de Dependencias Python

### 1. Instalar Dependencias Base

```bash
# Activar entorno virtual
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias OCR
pip install Pillow pytesseract PyMuPDF
```

### 2. Verificar Instalación

```bash
# Probar importaciones
python -c "import PIL; print('PIL OK')"
python -c "import pytesseract; print('pytesseract OK')"
python -c "import fitz; print('PyMuPDF OK')"
```

---

## ⚙️ Configuración del Servicio OCR

### 1. Configuración de Tesseract

El servicio OCR está configurado para usar:
- **Idiomas:** Español e inglés (`spa+eng`)
- **Modo OCR:** `--oem 3 --psm 6` (óptimo para facturas)
- **Formatos soportados:** JPG, JPEG, PNG, TIFF, BMP, PDF

### 2. Patrones de Extracción

El sistema utiliza patrones regex optimizados para facturas en español:

#### Montos
```python
amount_patterns = [
    r'total[:\s]*\$?[\s]*([0-9,]+\.?[0-9]*)',
    r'monto[:\s]*\$?[\s]*([0-9,]+\.?[0-9]*)',
    r'importe[:\s]*\$?[\s]*([0-9,]+\.?[0-9]*)',
    r'valor[:\s]*\$?[\s]*([0-9,]+\.?[0-9]*)',
    r'\$[\s]*([0-9,]+\.?[0-9]*)',
    r'([0-9,]+\.?[0-9]*)[\s]*pesos?',
]
```

#### Proveedores
```python
provider_patterns = [
    r'proveedor[:\s]*([^\n\r]+?)(?:\s+fecha|\s+total|\s+factura|$)',
    r'vendedor[:\s]*([^\n\r]+?)(?:\s+fecha|\s+total|\s+factura|$)',
    r'empresa[:\s]*([^\n\r]+?)(?:\s+fecha|\s+total|\s+factura|$)',
    r'razón social[:\s]*([^\n\r]+?)(?:\s+fecha|\s+total|\s+factura|$)',
]
```

#### Fechas
```python
date_patterns = [
    r'fecha[:\s]*([0-9]{4}[/\-\.][0-9]{1,2}[/\-\.][0-9]{1,2})',
    r'emisión[:\s]*([0-9]{4}[/\-\.][0-9]{1,2}[/\-\.][0-9]{1,2})',
    r'fecha[:\s]*([0-9]{1,2}[/\-\.][0-9]{1,2}[/\-\.][0-9]{2,4})',
    r'emisión[:\s]*([0-9]{1,2}[/\-\.][0-9]{1,2}[/\-\.][0-9]{2,4})',
    r'([0-9]{4}[/\-\.][0-9]{1,2}[/\-\.][0-9]{1,2})',
    r'([0-9]{1,2}[/\-\.][0-9]{1,2}[/\-\.][0-9]{2,4})',
]
```

#### Números de Factura
```python
invoice_number_patterns = [
    r'factura[:\s]*n[o°]?[:\s]*([0-9a-zA-Z\-]+)',
    r'no[:\s]*factura[:\s]*([0-9a-zA-Z\-]+)',
    r'comprobante[:\s]*n[o°]?[:\s]*([0-9a-zA-Z\-]+)',
]
```

---

## 🚀 Uso del Sistema OCR

### 1. Acceder a la Funcionalidad OCR

1. **Abrir el frontend:** http://localhost:5173
2. **Navegar a:** "Procesar Facturas con OCR"
3. **Seleccionar usuario** al que pertenece la factura
4. **Subir archivo** de la factura

### 2. Formatos Soportados

- **Imágenes:** JPG, JPEG, PNG, TIFF, BMP
- **Documentos:** PDF (con texto o escaneado)

### 3. Proceso de Procesamiento

1. **Subida de archivo:** El sistema valida el formato
2. **Extracción de texto:** Tesseract procesa la imagen/PDF
3. **Análisis de datos:** Patrones regex extraen información
4. **Cálculo de confianza:** Se evalúa la precisión de la extracción
5. **Edición manual:** Opción de corregir datos extraídos
6. **Creación de factura:** Se genera el registro en el sistema

---

## 📊 Nivel de Confianza

### Cálculo de Confianza

El sistema calcula un nivel de confianza (0.0 - 1.0) basado en:

- **Monto extraído:** 40% del peso
- **Proveedor extraído:** 30% del peso
- **Fecha extraída:** 20% del peso
- **Número de factura:** 10% del peso

### Interpretación de Confianza

- **0.8 - 1.0:** Excelente - Datos muy confiables
- **0.6 - 0.8:** Bueno - Revisar datos menores
- **0.4 - 0.6:** Regular - Revisar todos los datos
- **0.0 - 0.4:** Bajo - Revisión manual necesaria

---

## 🧪 Pruebas y Verificación

### 1. Probar el Servicio OCR

```bash
# Verificar que el servicio se carga correctamente
cd backend
source venv/bin/activate
python -c "from src.services.ocr_service import ocr_service; print('OCR Service OK')"
```

### 2. Probar Endpoints

```bash
# Verificar formatos soportados
curl http://localhost:8000/api/v1/ocr/supported-formats

# Respuesta esperada:
# {"supported_formats":[".jpg",".jpeg",".png",".tiff",".bmp",".pdf"],"description":"Formatos de archivo soportados para procesamiento OCR"}
```

### 3. Procesar Factura de Prueba

```bash
# Procesar una factura (reemplaza con archivo real)
curl -X POST "http://localhost:8000/api/v1/ocr/process" \
  -F "file=@factura_ejemplo.jpg" \
  -F "user_id=1"
```

---

## 🎯 Mejores Prácticas para Facturas

### 1. Calidad de Imagen

#### Para Mejores Resultados:
- **Resolución:** Mínimo 300 DPI
- **Iluminación:** Uniforme, sin sombras
- **Enfoque:** Texto nítido y legible
- **Orientación:** Correcta (no rotada)

#### Evitar:
- Imágenes borrosas o pixeladas
- Sombras o reflejos
- Texto cortado o parcialmente visible
- Imágenes muy pequeñas

### 2. Formato de Archivo

#### Recomendado:
- **PDF con texto:** Mejor precisión
- **PNG:** Buena calidad, sin compresión
- **TIFF:** Máxima calidad

#### Aceptable:
- **JPG:** Buena calidad, compresión mínima

#### Evitar:
- Archivos muy comprimidos
- Formatos no soportados

### 3. Contenido de la Factura

#### Para Mejor Extracción:
- **Monto:** Claramente visible con símbolo de moneda
- **Proveedor:** Nombre completo y legible
- **Fecha:** Formato estándar (DD/MM/YYYY)
- **Número:** Secuencial y visible

---

## 🔧 Configuración Avanzada

### 1. Personalizar Patrones

Puedes modificar los patrones de extracción en `backend/src/services/ocr_service.py`:

```python
# Agregar nuevos patrones para montos
self.patterns['amount'].append(r'nuevo_patron[:\s]*([0-9,]+\.?[0-9]*)')
```

### 2. Configurar Idiomas Adicionales

```python
# En extract_text_from_image()
text = pytesseract.image_to_string(
    image, 
    config=self.tesseract_config,
    lang='spa+eng+fra'  # Agregar francés
)
```

### 3. Ajustar Configuración de Tesseract

```python
# En __init__()
self.tesseract_config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,:-$'
```

---

## 🚨 Solución de Problemas

### Error: "tesseract is not installed or it's not in your PATH"

**Problema:** Tesseract no está instalado o no está en el PATH.

**Solución:**
1. Instalar Tesseract según las instrucciones anteriores
2. Verificar que esté en el PATH: `tesseract --version`
3. En Windows, reiniciar la terminal después de instalar

### Error: "No module named 'PIL'"

**Problema:** Pillow no está instalado.

**Solución:**
```bash
pip install Pillow
```

### Error: "Cannot identify image file"

**Problema:** El archivo no es una imagen válida.

**Solución:**
1. Verificar que el archivo no esté corrupto
2. Verificar que sea un formato soportado
3. Intentar con otro archivo

### Baja Precisión en la Extracción

**Problema:** Los datos extraídos no son precisos.

**Soluciones:**
1. **Mejorar calidad de imagen:** Usar mejor resolución e iluminación
2. **Ajustar patrones:** Modificar regex para tu tipo de facturas
3. **Usar edición manual:** Corregir datos después de la extracción
4. **Entrenar Tesseract:** Crear datos de entrenamiento específicos

---

## 📈 Monitoreo y Métricas

### 1. Logs del Sistema

Revisa los logs del servidor para:
- Errores de procesamiento
- Tiempo de procesamiento
- Niveles de confianza

### 2. Estadísticas de Uso

El sistema registra:
- Número de facturas procesadas
- Tiempo promedio de procesamiento
- Distribución de niveles de confianza
- Errores más comunes

### 3. Dashboard de OCR

En el frontend puedes ver:
- Facturas procesadas recientemente
- Niveles de confianza promedio
- Estadísticas de uso por usuario

---

## 🔄 Actualizaciones y Mantenimiento

### 1. Actualizar Tesseract

```bash
# macOS
brew upgrade tesseract

# Ubuntu/Debian
sudo apt update && sudo apt upgrade tesseract-ocr
```

### 2. Actualizar Dependencias Python

```bash
pip install --upgrade Pillow pytesseract PyMuPDF
```

### 3. Optimizar Patrones

Revisa regularmente los patrones de extracción y ajústalos según:
- Nuevos formatos de facturas
- Cambios en proveedores
- Feedback de usuarios

---

**¡Sistema OCR configurado y listo para procesar facturas físicas automáticamente! 🎉**
