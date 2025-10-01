# Control de Facturas Boosting

Sistema completo de gestión de facturas con procesamiento OCR, integración Gmail y análisis de datos.

## 🚀 Características Principales

- **Procesamiento OCR**: Extracción automática de datos de facturas usando Tesseract
- **Integración Gmail**: Sincronización automática de facturas desde Gmail
- **Dashboard Analytics**: Análisis y visualización de datos de facturas
- **Gestión de Usuarios**: Sistema de autenticación y autorización
- **Exportación Excel**: Generación de reportes en formato Excel
- **API REST**: Backend completo con FastAPI
- **Frontend React**: Interfaz moderna y responsiva

## 🏗️ Arquitectura

### Backend (FastAPI)
- **Framework**: FastAPI con Python 3.12
- **Base de Datos**: PostgreSQL con SQLAlchemy ORM
- **Autenticación**: JWT con bcrypt
- **OCR**: Tesseract con soporte para español e inglés
- **Integración**: Gmail API para sincronización automática
- **Tareas Asíncronas**: Celery con Redis

### Frontend (React + TypeScript)
- **Framework**: React 18 con TypeScript
- **Estilos**: Tailwind CSS
- **Estado**: Context API
- **HTTP Client**: Axios
- **Build Tool**: Vite

### Infraestructura
- **Contenedores**: Docker y Docker Compose
- **CI/CD**: GitHub Actions
- **Cloud**: Google Cloud Platform (Cloud Run, Cloud SQL, Cloud Storage)
- **Monitoreo**: Health checks y logging

## 📋 Prerrequisitos

- Python 3.12+
- Node.js 18+
- PostgreSQL 15+
- Docker (opcional)
- Tesseract OCR
- Cuenta de Google Cloud Platform (para producción)

## 🛠️ Instalación Local

### 1. Clonar el Repositorio
```bash
git clone https://github.com/AlejandroPODropi/facturasBst.git
cd facturasBst
```

### 2. Configurar Backend

#### Crear Entorno Virtual
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

#### Instalar Dependencias
```bash
pip install -r requirements.txt
```

#### Configurar Base de Datos
```bash
# Crear base de datos PostgreSQL
createdb facturas_boosting

# Ejecutar migraciones
alembic upgrade head
```

#### Configurar Variables de Entorno
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

#### Iniciar Servidor
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Configurar Frontend

#### Instalar Dependencias
```bash
cd frontend
npm install
```

#### Iniciar Servidor de Desarrollo
```bash
npm run dev
```

### 4. Configurar OCR

#### Instalar Tesseract
```bash
# macOS
brew install tesseract tesseract-lang

# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng

# Windows
# Descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
```

## 🐳 Instalación con Docker

### Usar Docker Compose
```bash
# Construir y ejecutar todos los servicios
docker-compose up --build

# Ejecutar en segundo plano
docker-compose up -d
```

### Servicios Incluidos
- **Backend**: Puerto 8000
- **Frontend**: Puerto 3000
- **PostgreSQL**: Puerto 5432
- **Redis**: Puerto 6379

## ☁️ Despliegue en Producción

### Google Cloud Platform

#### 1. Configurar Proyecto GCP
```bash
# Instalar gcloud CLI
# Configurar proyecto
gcloud config set project facturasbst

# Habilitar APIs necesarias
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

#### 2. Desplegar con Script Automatizado
```bash
# Ejecutar script de despliegue
./scripts/deploy-gcp.sh
```

#### 3. Configurar CI/CD

##### Actualizar Token de GitHub
1. Ir a GitHub Settings > Developer settings > Personal access tokens
2. Crear nuevo token con scope `workflow`
3. Actualizar el token en tu configuración local

##### Configurar Secrets de GitHub
```bash
# Agregar secrets en GitHub repository settings
GCP_SA_KEY: Contenido del archivo gcp-key.json
GCP_PROJECT_ID: facturasbst
GCP_REGION: us-central1
```

##### Agregar Workflows Manualmente
Los archivos de GitHub Actions están listos en `.github/workflows/` pero necesitan ser agregados manualmente debido a limitaciones del token.

## 📚 Documentación

**Toda la documentación está organizada en la carpeta [`documentos/`](documentos/)**

### Documentos Principales:
- [📖 Índice Completo de Documentación](documentos/README.md)
- [📘 README Actualizado (Versión Completa)](documentos/README_ACTUALIZADO.md)
- [🚀 Guía de Instalación](documentos/INSTALACION.md)
- [⚙️ Configuración Gmail](documentos/CONFIGURACION_GMAIL.md)
- [🔍 Configuración OCR](documentos/CONFIGURACION_OCR.md)
- [☁️ Despliegue en Producción](documentos/DESPLIEGUE_PRODUCCION.md)
- [🌐 Despliegue GCP](documentos/DESPLIEGUE_GCP.md)
- [🔧 Troubleshooting](documentos/TROUBLESHOOTING.md)
- [📊 Resumen Ejecutivo](documentos/RESUMEN_EJECUTIVO.md)
- [🗄️ Configuración de Base de Datos](documentos/CONFIGURACION_BASE_DATOS.md)
- [🔨 Solución Problema Base de Datos](documentos/SOLUCION_PROBLEMA_BASE_DATOS.md)
- [📜 Historial de Desarrollo](documentos/HISTORIAL_DESARROLLO_Y_PROBLEMAS.md)

## 🧪 Testing

### Backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend
npm test
```

## 📊 API Endpoints

### Autenticación
- `POST /auth/login` - Iniciar sesión
- `POST /auth/register` - Registrar usuario
- `POST /auth/refresh` - Renovar token

### Usuarios
- `GET /users/` - Listar usuarios
- `GET /users/{id}` - Obtener usuario
- `PUT /users/{id}` - Actualizar usuario
- `DELETE /users/{id}` - Eliminar usuario

### Facturas
- `GET /invoices/` - Listar facturas
- `POST /invoices/` - Crear factura
- `GET /invoices/{id}` - Obtener factura
- `PUT /invoices/{id}` - Actualizar factura
- `DELETE /invoices/{id}` - Eliminar factura

### OCR
- `POST /ocr/process` - Procesar imagen con OCR
- `GET /ocr/status/{task_id}` - Estado del procesamiento

### Gmail
- `GET /gmail/auth` - Iniciar autenticación Gmail
- `POST /gmail/callback` - Callback de autenticación
- `GET /gmail/sync` - Sincronizar facturas

### Dashboard
- `GET /dashboard/stats` - Estadísticas generales
- `GET /dashboard/analytics` - Análisis detallados

## 🔧 Configuración de Variables de Entorno

### Backend (.env)
```env
# Base de datos
DATABASE_URL=postgresql://user:password@localhost:5432/facturas_boosting

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Gmail API
GMAIL_CLIENT_ID=your-client-id
GMAIL_CLIENT_SECRET=your-client-secret
GMAIL_REDIRECT_URI=http://localhost:8000/gmail/callback

# OCR
TESSERACT_CMD=/usr/bin/tesseract

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Control de Facturas Boosting
```

## 🚨 Troubleshooting

### Problemas Comunes

#### Error de Tesseract
```bash
# Verificar instalación
tesseract --version

# Instalar paquetes de idioma
sudo apt-get install tesseract-ocr-spa tesseract-ocr-eng
```

#### Error de Base de Datos
```bash
# Verificar conexión
psql -h localhost -U user -d facturas_boosting

# Ejecutar migraciones
alembic upgrade head
```

#### Error de Gmail API
1. Verificar credenciales en Google Cloud Console
2. Habilitar Gmail API
3. Configurar OAuth 2.0 correctamente

## 📈 Roadmap

### Versión 1.1
- [ ] Mejoras en OCR con IA
- [ ] Integración con más proveedores de email
- [ ] Dashboard avanzado con gráficos
- [ ] Notificaciones push

### Versión 1.2
- [ ] API móvil
- [ ] Integración con sistemas contables
- [ ] Análisis predictivo
- [ ] Multi-tenancy

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👥 Equipo

- **Desarrollo**: Alejandro PODropi
- **Arquitectura**: FastAPI + React
- **DevOps**: Google Cloud Platform

## 🌐 URLs de Producción

### 🎉 Última Actualización: Fix CORS y Endpoints (v2.0.1)
**Fecha:** 1 de Octubre de 2025  
**Estado:** ✅ **DESPLEGADO EXITOSAMENTE**

- **Frontend:** https://frontend-493189429371.us-central1.run.app
- **Backend:** https://backend-493189429371.us-central1.run.app
- **API Docs:** https://backend-493189429371.us-central1.run.app/docs
- **Health Check:** https://backend-493189429371.us-central1.run.app/health

### 📱 Características Implementadas

#### **Diseño Responsive (v2.0.0)**
- 📱 **Móviles** (< 640px): Sidebar colapsable, vista de tarjetas
- 📱 **Tablets** (640px - 1024px): Layout adaptativo, tablas optimizadas  
- 💻 **Desktop** (> 1024px): Vista completa con sidebar fijo

#### **Fix CORS y Endpoints (v2.0.1)**
- ✅ CORS configurado para `facturas.boostingsas.com`
- ✅ Router de Gmail habilitado (endpoints `/stats` y `/auth/status`)
- ✅ Error 500 en dashboard stats corregido
- ✅ Archivo `vite.svg` agregado

**Mejoras implementadas:**
- ✅ Sidebar colapsable con hamburger menu
- ✅ Formularios touch-friendly (inputs ≥44px)
- ✅ Vista dual: tablas en desktop, tarjetas en móviles
- ✅ Dashboard con grids adaptativos
- ✅ Navegación optimizada para todos los dispositivos
- ✅ Todos los endpoints funcionando correctamente
- ✅ Sin errores CORS en producción

**Ver documentación completa:**
- [`documentos/DESPLEGUE_RESPONSIVE_COMPLETO.md`](documentos/DESPLEGUE_RESPONSIVE_COMPLETO.md)
- [`documentos/SOLUCION_ERRORES_CORS_ENDPOINTS.md`](documentos/SOLUCION_ERRORES_CORS_ENDPOINTS.md)

## 📞 Soporte

Para soporte técnico o preguntas:
- Crear issue en GitHub
- Revisar documentación en `/documentos`
- Consultar troubleshooting guide

---

**Control de Facturas Boosting** - Sistema profesional de gestión de facturas con tecnología de vanguardia y diseño responsive.
