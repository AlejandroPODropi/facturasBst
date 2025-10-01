# 🔧 Guía de Solución de Problemas

## 🎯 Problemas Comunes y Soluciones

Esta guía te ayudará a resolver los problemas más frecuentes al instalar y ejecutar el Sistema de Control de Facturas Boosting.

---

## 🐍 Problemas de Python y Entornos Virtuales

### Error: "ModuleNotFoundError: No module named 'PIL'"

**Síntomas:**
```
ModuleNotFoundError: No module named 'PIL'
```

**Causa:** Pillow no está instalado en el entorno virtual correcto.

**Solución:**
```bash
# Verificar entorno virtual activo
which python

# Instalar PIL en el entorno correcto
pip install Pillow pytesseract PyMuPDF

# Verificar instalación
python -c "import PIL; print('PIL OK')"
```

### Error: "No module named 'pytesseract'"

**Síntomas:**
```
ModuleNotFoundError: No module named 'pytesseract'
```

**Causa:** pytesseract no está instalado.

**Solución:**
```bash
pip install pytesseract
```

### Error: "No module named 'fitz'"

**Síntomas:**
```
ModuleNotFoundError: No module named 'fitz'
```

**Causa:** PyMuPDF no está instalado.

**Solución:**
```bash
pip install PyMuPDF
```

### Error: "venv/bin/activate: No such file or directory"

**Síntomas:**
```
bash: venv/bin/activate: No such file or directory
```

**Causa:** El entorno virtual no existe o está en una ubicación diferente.

**Solución:**
```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate     # Windows
```

---

## 🔍 Problemas de Tesseract OCR

### Error: "tesseract is not installed or it's not in your PATH"

**Síntomas:**
```
TesseractNotFoundError: tesseract is not installed or it's not in your PATH
```

**Causa:** Tesseract no está instalado o no está en el PATH del sistema.

**Solución:**

#### macOS
```bash
# Instalar con Homebrew
brew install tesseract

# Verificar instalación
tesseract --version
```

#### Ubuntu/Debian
```bash
# Instalar Tesseract
sudo apt update
sudo apt install tesseract-ocr

# Verificar instalación
tesseract --version
```

#### Windows
1. Descargar e instalar desde: https://github.com/UB-Mannheim/tesseract/wiki
2. Agregar al PATH del sistema
3. Reiniciar la terminal

### Error: "TesseractError: (1, 'Error opening data file')"

**Síntomas:**
```
TesseractError: (1, 'Error opening data file /usr/share/tesseract-ocr/4.00/tessdata/spa.traineddata')
```

**Causa:** Faltan archivos de idioma para Tesseract.

**Solución:**

#### macOS
```bash
brew install tesseract-lang
```

#### Ubuntu/Debian
```bash
sudo apt install tesseract-ocr-spa  # Para español
sudo apt install tesseract-ocr-eng  # Para inglés
```

---

## 🗄️ Problemas de Base de Datos

### Error: "connection to server at 'localhost' (127.0.0.1), port 5432 failed"

**Síntomas:**
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection to server at 'localhost' (127.0.0.1), port 5432 failed
```

**Causa:** PostgreSQL no está ejecutándose o no está configurado correctamente.

**Solución:**
1. **Verificar que PostgreSQL esté ejecutándose:**
   ```bash
   # macOS
   brew services start postgresql
   
   # Ubuntu/Debian
   sudo systemctl start postgresql
   sudo systemctl enable postgresql
   ```

2. **Verificar configuración en .env:**
   ```env
   DATABASE_URL=postgresql://usuario:password@localhost:5432/facturas_boosting
   ```

3. **Crear base de datos si no existe:**
   ```sql
   CREATE DATABASE facturas_boosting;
   ```

### Error: "database 'facturas_boosting' does not exist"

**Síntomas:**
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) FATAL: database "facturas_boosting" does not exist
```

**Causa:** La base de datos no ha sido creada.

**Solución:**
```sql
-- Conectar a PostgreSQL
psql -U postgres

-- Crear base de datos
CREATE DATABASE facturas_boosting;

-- Crear usuario
CREATE USER boosting_user WITH PASSWORD 'tu_password';

-- Otorgar permisos
GRANT ALL PRIVILEGES ON DATABASE facturas_boosting TO boosting_user;
```

### Error: "relation 'users' does not exist"

**Síntomas:**
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedTable) relation "users" does not exist
```

**Causa:** Las migraciones no se han ejecutado.

**Solución:**
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

---

## 🌐 Problemas de Red y Puertos

### Error: "Address already in use"

**Síntomas:**
```
ERROR: [Errno 48] Address already in use
```

**Causa:** El puerto 8000 ya está siendo usado por otro proceso.

**Solución:**
```bash
# Encontrar proceso usando el puerto
lsof -i :8000

# Detener proceso específico
pkill -f "uvicorn src.main:app"

# O usar puerto diferente
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

### Error: "Connection refused"

**Síntomas:**
```
curl: (7) Failed to connect to localhost port 8000: Connection refused
```

**Causa:** El servidor backend no está ejecutándose.

**Solución:**
```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📧 Problemas de Gmail API

### Error: "Access blocked: This app's request is invalid"

**Síntomas:**
```
Access blocked: This app's request is invalid
```

**Causa:** La aplicación no está verificada por Google o no está configurada correctamente.

**Solución:**
1. **Verificar configuración en Google Cloud Console:**
   - Ve a Google Cloud Console > APIs y servicios > Pantalla de consentimiento
   - Agrega tu email como usuario de prueba
   - O solicita verificación de la aplicación

2. **Verificar archivo credentials.json:**
   - Asegúrate de que esté en la raíz del proyecto backend
   - Verifica que no esté corrupto

### Error: "The OAuth client was not found"

**Síntomas:**
```
The OAuth client was not found
```

**Causa:** El archivo credentials.json no está en la ubicación correcta o está corrupto.

**Solución:**
1. **Verificar ubicación:**
   ```bash
   ls -la backend/credentials.json
   ```

2. **Regenerar credenciales:**
   - Ve a Google Cloud Console > APIs y servicios > Credenciales
   - Elimina las credenciales existentes
   - Crea nuevas credenciales OAuth 2.0
   - Descarga el nuevo archivo JSON

### Error: "Token has been expired or revoked"

**Síntomas:**
```
Token has been expired or revoked
```

**Causa:** El token de acceso ha expirado.

**Solución:**
```bash
# Eliminar token existente
rm backend/token.json

# Ejecutar autenticación nuevamente
curl -X POST http://localhost:8000/api/v1/gmail/auth/authenticate
```

---

## 🔍 Problemas de OCR

### Error: "Cannot identify image file"

**Síntomas:**
```
PIL.UnidentifiedImageError: cannot identify image file
```

**Causa:** El archivo no es una imagen válida o está corrupto.

**Solución:**
1. **Verificar formato de archivo:**
   - Asegúrate de que sea JPG, PNG, PDF, TIFF o BMP
   - Verifica que el archivo no esté corrupto

2. **Probar con otro archivo:**
   - Usa una imagen de prueba conocida
   - Verifica que la imagen se pueda abrir en un visor

### Error: "No se pudo extraer texto del archivo"

**Síntomas:**
```
ValueError: No se pudo extraer texto del archivo
```

**Causa:** La imagen no contiene texto legible o la calidad es muy baja.

**Solución:**
1. **Mejorar calidad de imagen:**
   - Usar mejor resolución (mínimo 300 DPI)
   - Mejorar iluminación
   - Asegurar que el texto sea nítido

2. **Verificar contenido:**
   - Asegúrate de que la imagen contenga texto
   - Verifica que el texto sea legible

### Baja Precisión en la Extracción

**Síntomas:** Los datos extraídos no son precisos o están incompletos.

**Causa:** Calidad de imagen insuficiente o patrones de extracción no optimizados.

**Solución:**
1. **Mejorar calidad de imagen:**
   - Usar mejor resolución
   - Mejorar iluminación
   - Evitar sombras y reflejos

2. **Ajustar patrones:**
   - Modificar patrones regex en `ocr_service.py`
   - Agregar patrones específicos para tu tipo de facturas

---

## 🖥️ Problemas de Frontend

### Error: "Module not found: Can't resolve"

**Síntomas:**
```
Module not found: Can't resolve 'react-query'
```

**Causa:** Dependencias de Node.js no instaladas.

**Solución:**
```bash
cd frontend
npm install
```

### Error: "TypeScript compilation failed"

**Síntomas:**
```
TypeScript compilation failed
```

**Causa:** Errores de tipos en TypeScript.

**Solución:**
```bash
# Verificar errores específicos
npm run build

# Arreglar errores de tipos
# O usar modo desarrollo que es más permisivo
npm run dev
```

### Error: "Port 5173 is already in use"

**Síntomas:**
```
Port 5173 is already in use
```

**Causa:** El puerto del frontend ya está siendo usado.

**Solución:**
```bash
# Usar puerto diferente
npm run dev -- --port 5174
```

---

## 🔧 Problemas de Configuración

### Error: "Environment variable not found"

**Síntomas:**
```
Environment variable 'DATABASE_URL' not found
```

**Causa:** Variables de entorno no configuradas.

**Solución:**
1. **Crear archivo .env:**
   ```bash
   cp .env.example .env
   ```

2. **Configurar variables:**
   ```env
   DATABASE_URL=postgresql://usuario:password@localhost:5432/facturas_boosting
   GMAIL_CREDENTIALS_FILE=credentials.json
   ```

### Error: "Permission denied"

**Síntomas:**
```
Permission denied: '/path/to/uploads'
```

**Causa:** Permisos insuficientes en directorios.

**Solución:**
```bash
# Crear directorio de uploads
mkdir -p backend/uploads

# Otorgar permisos
chmod 755 backend/uploads
```

---

## 📊 Verificación del Sistema

### Comandos de Verificación

```bash
# Verificar backend
curl http://localhost:8000/health

# Verificar OCR
curl http://localhost:8000/api/v1/ocr/supported-formats

# Verificar Gmail
curl http://localhost:8000/api/v1/gmail/auth/status

# Verificar base de datos
cd backend
source venv/bin/activate
python -c "from src.database import engine; print('DB OK')"
```

### Logs Útiles

```bash
# Ver logs del servidor
tail -f backend/logs/app.log

# Ver logs de errores
grep "ERROR" backend/logs/app.log
```

---

## 🆘 Obtener Ayuda

### 1. Verificar Documentación
- [Guía de Instalación](INSTALACION.md)
- [Configuración Gmail API](CONFIGURACION_GMAIL.md)
- [Configuración OCR](CONFIGURACION_OCR.md)

### 2. Verificar Logs
- Revisar logs del servidor backend
- Verificar logs del navegador (F12)
- Revisar logs de la base de datos

### 3. Contactar Soporte
- Incluir mensaje de error completo
- Incluir pasos para reproducir el problema
- Incluir información del sistema (OS, versiones)

---

**¡Con esta guía deberías poder resolver la mayoría de problemas comunes! 🔧**
