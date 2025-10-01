# 📋 Guía de Instalación - Sistema de Control de Facturas Boosting

## 🎯 Resumen del Sistema

Sistema completo de gestión de facturas desarrollado para Boosting que incluye:
- **Backend:** FastAPI con PostgreSQL
- **Frontend:** React + TypeScript
- **OCR:** Procesamiento de facturas físicas con Tesseract
- **Gmail API:** Procesamiento automático de facturas electrónicas
- **Dashboard:** Estadísticas en tiempo real

---

## 🔧 Requisitos Previos

### Software Necesario
- **Python 3.8+** (recomendado 3.12)
- **Node.js 16+** (recomendado 18+)
- **PostgreSQL 12+**
- **Git**

### Herramientas del Sistema
- **Tesseract OCR** (para procesamiento de imágenes)
- **Google Cloud Console** (para Gmail API)

---

## 📦 Instalación Paso a Paso

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd facturasBst
```

### 2. Configurar Base de Datos PostgreSQL

```sql
-- Crear base de datos
CREATE DATABASE facturas_boosting;

-- Crear usuario
CREATE USER boosting_user WITH PASSWORD 'tu_password_seguro';

-- Otorgar permisos
GRANT ALL PRIVILEGES ON DATABASE facturas_boosting TO boosting_user;
```

### 3. Instalar Tesseract OCR

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

### 4. Configurar Backend

```bash
# Navegar al directorio backend
cd backend

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar dependencias OCR adicionales
pip install Pillow pytesseract PyMuPDF
```

### 5. Configurar Variables de Entorno

Crear archivo `.env` en el directorio `backend/`:

```env
# Base de datos
DATABASE_URL=postgresql://boosting_user:tu_password_seguro@localhost:5432/facturas_boosting

# Gmail API (opcional)
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json
GMAIL_SCOPES=https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.modify
```

### 6. Ejecutar Migraciones de Base de Datos

```bash
# Desde el directorio backend
cd backend
source venv/bin/activate

# Ejecutar migraciones
alembic upgrade head
```

### 7. Configurar Frontend

```bash
# Navegar al directorio frontend
cd frontend

# Instalar dependencias
npm install
```

### 8. Configurar Gmail API (Opcional)

#### 8.1 Crear Proyecto en Google Cloud Console
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la **Gmail API**:
   - Ve a "APIs & Services" > "Library"
   - Busca "Gmail API"
   - Haz clic en "Enable"

#### 8.2 Configurar OAuth 2.0
1. Ve a "APIs & Services" > "Credentials"
2. Haz clic en "Create Credentials" > "OAuth client ID"
3. Selecciona "Desktop application"
4. Descarga el archivo JSON de credenciales
5. Renómbralo a `credentials.json` y colócalo en la raíz del proyecto backend

---

## 🚀 Ejecutar el Sistema

### Opción 1: Ejecutar desde la Raíz del Proyecto

```bash
# Activar entorno virtual de la raíz
source venv/bin/activate

# Instalar dependencias OCR en el entorno de la raíz
pip install Pillow pytesseract PyMuPDF

# Ejecutar backend
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

En otra terminal:
```bash
# Ejecutar frontend
cd frontend
npm run dev
```

### Opción 2: Ejecutar desde Directorios Específicos

#### Backend
```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm run dev
```

---

## 🌐 Acceso al Sistema

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **Documentación API:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🧪 Verificar Instalación

### 1. Verificar Backend
```bash
curl http://localhost:8000/health
# Debe responder: {"status":"healthy","service":"control-facturas-boosting"}
```

### 2. Verificar OCR
```bash
curl http://localhost:8000/api/v1/ocr/supported-formats
# Debe responder con los formatos soportados
```

### 3. Verificar Gmail API
```bash
curl http://localhost:8000/api/v1/gmail/auth/status
# Debe responder con el estado de autenticación
```

---

## 🔧 Solución de Problemas Comunes

### Error: "ModuleNotFoundError: No module named 'PIL'"

**Problema:** PIL no está instalado en el entorno virtual correcto.

**Solución:**
```bash
# Verificar entorno virtual activo
which python

# Instalar PIL en el entorno correcto
pip install Pillow pytesseract PyMuPDF
```

### Error: "Address already in use"

**Problema:** El puerto 8000 ya está en uso.

**Solución:**
```bash
# Detener procesos en el puerto 8000
pkill -f "uvicorn src.main:app"

# O usar un puerto diferente
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

### Error: "No module named 'tesseract'"

**Problema:** Tesseract no está instalado en el sistema.

**Solución:**
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt install tesseract-ocr

# Verificar instalación
tesseract --version
```

### Error de Conexión a Base de Datos

**Problema:** PostgreSQL no está ejecutándose o las credenciales son incorrectas.

**Solución:**
1. Verificar que PostgreSQL esté ejecutándose
2. Verificar las credenciales en el archivo `.env`
3. Verificar que la base de datos existe

---

## 📊 Estructura del Proyecto

```
facturasBst/
├── backend/
│   ├── src/
│   │   ├── routers/          # Endpoints de la API
│   │   ├── services/         # Lógica de negocio
│   │   ├── models.py         # Modelos de base de datos
│   │   ├── schemas.py        # Esquemas Pydantic
│   │   └── main.py          # Punto de entrada
│   ├── tests/               # Pruebas unitarias
│   ├── venv/               # Entorno virtual del backend
│   └── requirements.txt     # Dependencias Python
├── frontend/
│   ├── src/
│   │   ├── components/      # Componentes React
│   │   ├── pages/          # Páginas de la aplicación
│   │   ├── services/       # Cliente API
│   │   └── types/          # Tipos TypeScript
│   └── package.json        # Dependencias Node.js
├── venv/                   # Entorno virtual de la raíz
├── task/                   # Documentación del proyecto
└── README.md              # Documentación principal
```

---

## 🎯 Funcionalidades Disponibles

### ✅ MVP Fase 1 - Completado
- [x] Sistema completo de gestión de facturas
- [x] Backend FastAPI con PostgreSQL
- [x] Frontend React + TypeScript
- [x] Dashboard con estadísticas en tiempo real
- [x] Gestión completa de usuarios y facturas
- [x] Sistema de validación con visualizador de archivos
- [x] Exportación a Excel con filtros personalizables

### ✅ Fase 2 - Completado
- [x] **Integración Gmail API:** Procesamiento automático de facturas electrónicas
- [x] **OCR para Facturas Físicas:** Procesamiento de imágenes y PDFs
- [x] **Componente reactivado:** Funcionalidad OCR completamente operativa

---

## 🔄 Próximos Pasos

1. **Procesamiento asíncrono con Celery** - Para manejar OCR y Gmail en background
2. **Notificaciones automáticas** - Por email cuando se procesen facturas
3. **Autenticación y autorización** - Sistema de login y roles
4. **App móvil** - React Native para colaboradores en campo

---

## 📞 Soporte

Para problemas o preguntas:
1. Revisar esta documentación
2. Verificar los logs del servidor
3. Consultar la documentación de la API en `/docs`
4. Contactar al equipo de desarrollo

---

**¡Sistema de Control de Facturas para Boosting - Listo para Producción! 🎉**
