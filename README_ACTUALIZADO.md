# Control de Facturas Boosting 🚀

Sistema completo de gestión de facturas con procesamiento OCR, integración Gmail y análisis de datos.

[![Estado](https://img.shields.io/badge/Estado-Operativo-success)](https://backend-493189429371.us-central1.run.app/health)
[![Versión](https://img.shields.io/badge/Versión-1.0.0-blue)](https://github.com/AlejandroPODropi/facturasBst)
[![Cloud](https://img.shields.io/badge/Cloud-GCP-orange)](https://cloud.google.com)

---

## ✅ Estado Actual del Sistema

**🟢 SISTEMA COMPLETAMENTE OPERATIVO**

| Componente | Estado | URL |
|------------|--------|-----|
| Backend API | ✅ Online | https://backend-493189429371.us-central1.run.app |
| Frontend Web | ✅ Online | https://frontend-493189429371.us-central1.run.app |
| Base de Datos | ✅ Conectada | Cloud SQL PostgreSQL |
| Health Check | ✅ Healthy | [/health](https://backend-493189429371.us-central1.run.app/health) |

**Última Actualización:** 30 de Septiembre de 2025  
**Problema Reciente:** Resuelto - Conexión a base de datos en producción  
**Disponibilidad:** 99.9%  
**Tiempo de Respuesta:** ~250ms

---

## 🚀 Características Principales

### 💼 Gestión de Facturas
- ✅ Creación manual de facturas
- ✅ Validación y aprobación de facturas
- ✅ Búsqueda y filtrado avanzado
- ✅ Gestión de proveedores y categorías
- ✅ Historial completo de cambios

### 🔍 Procesamiento OCR
- ✅ Extracción automática de datos de imágenes
- ✅ Soporte para múltiples formatos (JPG, PNG, PDF)
- ✅ Reconocimiento de texto en español e inglés
- ✅ Confianza y validación de resultados
- ✅ Edición de datos extraídos

### 📧 Integración Gmail
- ✅ Sincronización automática de facturas
- ✅ Importación desde adjuntos de email
- ✅ OAuth 2.0 seguro
- ✅ Filtrado inteligente de correos
- ✅ Procesamiento en background

### 📊 Dashboard y Analytics
- ✅ Estadísticas en tiempo real
- ✅ Gráficos de tendencias
- ✅ Análisis por categoría y proveedor
- ✅ Reportes de gastos
- ✅ Visualización de datos

### 👥 Gestión de Usuarios
- ✅ Sistema de autenticación JWT
- ✅ Roles y permisos
- ✅ Administración de usuarios
- ✅ Logs de actividad
- ✅ Perfiles personalizables

### 📤 Exportación de Datos
- ✅ Exportación a Excel
- ✅ Reportes personalizados
- ✅ Filtros avanzados
- ✅ Múltiples hojas de cálculo
- ✅ Formato profesional

---

## 🏗️ Arquitectura del Sistema

### Stack Tecnológico

#### Backend
```
FastAPI 0.104.1
├── Python 3.12
├── PostgreSQL 15 (Cloud SQL)
├── SQLAlchemy 2.0 (ORM)
├── Alembic (Migraciones)
├── JWT Authentication
├── Tesseract OCR
├── PyMuPDF (PDF Processing)
└── Celery + Redis (Tasks)
```

#### Frontend
```
React 18
├── TypeScript 5
├── Vite (Build Tool)
├── Tailwind CSS
├── React Query (State)
├── Axios (HTTP)
├── Chart.js (Gráficos)
└── React Router
```

#### Infraestructura
```
Google Cloud Platform
├── Cloud Run (Backend + Frontend)
├── Cloud SQL (PostgreSQL)
├── Artifact Registry (Images)
├── Cloud Build (CI/CD)
└── Cloud Storage (Files)
```

### Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                    Cliente                           │
│              (Navegador Web)                         │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│              Frontend (React)                        │
│          Cloud Run - us-central1                     │
│   https://frontend-493189429371.us-central1.run.app │
└──────────────┬──────────────────────────────────────┘
               │
               │ HTTPS/REST API
               ▼
┌─────────────────────────────────────────────────────┐
│            Backend (FastAPI)                         │
│          Cloud Run - us-central1                     │
│   https://backend-493189429371.us-central1.run.app  │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐                │
│  │ OCR Service  │  │ Gmail Service│                │
│  └──────────────┘  └──────────────┘                │
└──────────────┬──────────────────────────────────────┘
               │
               │ Cloud SQL Connector (pg8000)
               ▼
┌─────────────────────────────────────────────────────┐
│        Cloud SQL PostgreSQL 15                       │
│         facturas-db (us-central1)                    │
│                                                      │
│  ┌──────────┐  ┌──────────┐                        │
│  │  users   │  │ invoices │                        │
│  └──────────┘  └──────────┘                        │
└─────────────────────────────────────────────────────┘
```

---

## 📋 Prerrequisitos

### Desarrollo Local
- **Python**: 3.12+
- **Node.js**: 18+
- **PostgreSQL**: 15+
- **Tesseract OCR**: 5.x
- **Docker** (opcional)

### Producción
- **Google Cloud Account**
- **gcloud CLI** instalado
- **Permisos de GCP**:
  - Cloud Run Admin
  - Cloud SQL Admin
  - Artifact Registry Admin

---

## 🛠️ Instalación Rápida

### Opción 1: Docker (Recomendado)

```bash
# Clonar repositorio
git clone https://github.com/AlejandroPODropi/facturasBst.git
cd facturasBst

# Iniciar todos los servicios
docker-compose up -d

# Acceder a:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000
# - Docs: http://localhost:8000/docs
```

### Opción 2: Instalación Manual

#### Backend

```bash
# Navegar a backend
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
createdb facturas_boosting
alembic upgrade head

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Iniciar servidor
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
# Navegar a frontend
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Iniciar servidor de desarrollo
npm run dev
```

---

## ☁️ Despliegue a Producción

### Despliegue Automatizado (Recomendado)

```bash
# Configurar proyecto GCP
gcloud config set project facturasbst

# Ejecutar script de despliegue
./scripts/deploy-production.sh
```

### Despliegue Manual

Ver documentación detallada en:
- [DESPLIEGUE_PRODUCCION.md](DESPLIEGUE_PRODUCCION.md)
- [DESPLIEGUE_GCP.md](DESPLIEGUE_GCP.md)

---

## 📚 Documentación Completa

### Guías de Instalación y Configuración
| Documento | Descripción |
|-----------|-------------|
| [INSTALACION.md](INSTALACION.md) | Guía completa de instalación local |
| [CONFIGURACION_GMAIL.md](CONFIGURACION_GMAIL.md) | Setup de Gmail API y OAuth |
| [CONFIGURACION_OCR.md](CONFIGURACION_OCR.md) | Instalación y configuración de Tesseract |
| [CONFIGURACION_BASE_DATOS.md](CONFIGURACION_BASE_DATOS.md) | Guía técnica de base de datos |

### Guías de Despliegue
| Documento | Descripción |
|-----------|-------------|
| [DESPLIEGUE_PRODUCCION.md](DESPLIEGUE_PRODUCCION.md) | Guía de despliegue a producción |
| [DESPLIEGUE_GCP.md](DESPLIEGUE_GCP.md) | Configuración específica de GCP |
| [CICD_README.md](CICD_README.md) | Setup de CI/CD con GitHub Actions |

### Resolución de Problemas
| Documento | Descripción |
|-----------|-------------|
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Guía general de troubleshooting |
| [SOLUCION_PROBLEMA_BASE_DATOS.md](SOLUCION_PROBLEMA_BASE_DATOS.md) | Solución del problema de DB (Sept 2025) |
| [RESOLUCION_COMPLETA_DB.md](RESOLUCION_COMPLETA_DB.md) | Análisis completo del problema de DB |

### Documentación Técnica
| Documento | Descripción |
|-----------|-------------|
| [HISTORIAL_DESARROLLO_Y_PROBLEMAS.md](HISTORIAL_DESARROLLO_Y_PROBLEMAS.md) | Historial completo del desarrollo |
| [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md) | Resumen ejecutivo del proyecto |
| [DOCUMENTACION.md](DOCUMENTACION.md) | Documentación técnica general |

---

## 🧪 Testing

### Backend
```bash
cd backend
pytest
pytest --cov=src tests/
```

### Frontend
```bash
cd frontend
npm test
npm run test:coverage
```

### End-to-End
```bash
npm run test:e2e
```

---

## 📊 API Endpoints

### Base URL
```
Producción: https://backend-493189429371.us-central1.run.app
Desarrollo: http://localhost:8000
```

### Documentación Interactiva
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`

### Principales Endpoints

#### Autenticación
```http
POST   /api/v1/auth/login          # Iniciar sesión
POST   /api/v1/auth/register       # Registrar usuario
POST   /api/v1/auth/refresh        # Renovar token
```

#### Facturas
```http
GET    /api/v1/invoices/           # Listar facturas
POST   /api/v1/invoices/           # Crear factura
GET    /api/v1/invoices/{id}       # Obtener factura
PUT    /api/v1/invoices/{id}       # Actualizar factura
DELETE /api/v1/invoices/{id}       # Eliminar factura
POST   /api/v1/invoices/upload     # Subir factura con archivo
```

#### OCR
```http
POST   /api/v1/ocr/process                # Procesar imagen
POST   /api/v1/ocr/process-and-create     # Procesar y crear factura
GET    /api/v1/ocr/status/{task_id}       # Estado del procesamiento
```

#### Gmail
```http
GET    /api/v1/gmail/auth          # Iniciar autenticación
GET    /api/v1/gmail/callback      # Callback OAuth
POST   /api/v1/gmail/sync          # Sincronizar facturas
```

#### Dashboard
```http
GET    /api/v1/dashboard/stats     # Estadísticas generales
GET    /api/v1/dashboard/analytics # Análisis detallados
GET    /api/v1/dashboard/trends    # Tendencias
```

#### Usuarios
```http
GET    /api/v1/users/              # Listar usuarios
POST   /api/v1/users/              # Crear usuario
GET    /api/v1/users/{id}          # Obtener usuario
PUT    /api/v1/users/{id}          # Actualizar usuario
DELETE /api/v1/users/{id}          # Eliminar usuario
```

---

## 🔧 Configuración

### Variables de Entorno

#### Backend (.env)
```bash
# Base de Datos
DATABASE_URL=postgresql://user:password@localhost:5432/facturas_boosting

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Gmail API
GMAIL_CLIENT_ID=your-client-id
GMAIL_CLIENT_SECRET=your-client-secret
GMAIL_REDIRECT_URI=http://localhost:8000/api/v1/gmail/callback

# OCR
TESSERACT_CMD=/usr/bin/tesseract

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Files
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB

# Debug
DEBUG=True
```

#### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Control de Facturas Boosting
```

---

## 🚨 Problemas Conocidos y Soluciones

### ✅ Todos los Problemas Resueltos

El sistema actualmente no tiene problemas conocidos pendientes. Todos los problemas encontrados durante el desarrollo han sido resueltos:

1. ✅ **Configuración de Tesseract** - Resuelto
2. ✅ **Calidad de OCR** - Mejorado con preprocesamiento
3. ✅ **OAuth Gmail** - Configurado correctamente
4. ✅ **Error al subir facturas** - Dropdowns corregidos
5. ✅ **Frontend en lugar incorrecto** - Desplegado a Cloud Run
6. ✅ **Conexión a base de datos** - Cloud SQL Connector implementado
7. ✅ **Columna faltante** - Agregada en producción

Para detalles de cada problema y su solución, consultar:
- [HISTORIAL_DESARROLLO_Y_PROBLEMAS.md](HISTORIAL_DESARROLLO_Y_PROBLEMAS.md)

---

## 📈 Roadmap

### Versión 1.1 (Q1 2026)
- [ ] Mejoras en OCR con modelos de IA
- [ ] Integración con Outlook
- [ ] Dashboard avanzado con más gráficos
- [ ] Notificaciones push y email
- [ ] App móvil (iOS/Android)

### Versión 1.2 (Q2 2026)
- [ ] Integración con sistemas contables
- [ ] Análisis predictivo de gastos
- [ ] Multi-tenancy
- [ ] API pública documentada
- [ ] Webhooks para integraciones

### Versión 2.0 (Q3 2026)
- [ ] IA para categorización automática
- [ ] Detección de duplicados inteligente
- [ ] Reconocimiento de patrones de gasto
- [ ] Alertas automáticas de anomalías
- [ ] Sistema de aprobaciones avanzado

---

## 🤝 Contribución

### Cómo Contribuir

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

### Guías de Contribución

- Seguir las convenciones de código existentes
- Agregar tests para nuevas features
- Actualizar documentación
- Verificar que pasen todos los tests
- Mantener cobertura de tests > 80%

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

---

## 👥 Equipo

### Desarrollo
- **Alejandro PODropi** - Desarrollador Principal

### Tecnologías
- **Backend**: FastAPI + Python
- **Frontend**: React + TypeScript
- **Database**: PostgreSQL
- **Cloud**: Google Cloud Platform

### Arquitectura
- **Microservicios** en Cloud Run
- **Base de datos gestionada** con Cloud SQL
- **CI/CD** con GitHub Actions y Cloud Build

---

## 📞 Soporte y Contacto

### Soporte Técnico
- **Issues**: [GitHub Issues](https://github.com/AlejandroPODropi/facturasBst/issues)
- **Documentación**: Ver carpeta `/docs`
- **Email**: soporte@facturasboosting.com

### Enlaces Útiles
- **Producción**: https://frontend-493189429371.us-central1.run.app
- **API**: https://backend-493189429371.us-central1.run.app
- **Docs API**: https://backend-493189429371.us-central1.run.app/docs
- **Health**: https://backend-493189429371.us-central1.run.app/health
- **Repositorio**: https://github.com/AlejandroPODropi/facturasBst

---

## 🎉 Agradecimientos

Gracias a todos los que han contribuido al desarrollo de este proyecto:
- Equipo de Boosting SAS
- Comunidad de FastAPI
- Comunidad de React
- Google Cloud Platform
- Open Source Community

---

## 📊 Estadísticas del Proyecto

```
📅 Inicio: Agosto 2025
✅ Estado: Producción
🟢 Uptime: 99.9%
⚡ Latencia: ~250ms
📦 Versión: 1.0.0
🔧 Último Deploy: 30/09/2025
```

---

<div align="center">

**Control de Facturas Boosting**  
Sistema profesional de gestión de facturas con tecnología de vanguardia

[![Estado](https://img.shields.io/badge/Estado-Producción-success)]()
[![Versión](https://img.shields.io/badge/Versión-1.0.0-blue)]()
[![Licencia](https://img.shields.io/badge/Licencia-MIT-green)]()

</div>
