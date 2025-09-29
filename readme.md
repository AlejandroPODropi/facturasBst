# 🧾 Sistema de Control de Facturas para Boosting

Sistema completo de gestión de facturas desarrollado para Boosting. Incluye backend FastAPI con PostgreSQL, frontend React + TypeScript, sistema de validación con visualizador de archivos, gestión de usuarios y filtros avanzados.

## 🎯 **¡MVP Fase 1 y Fase 2 COMPLETADOS AL 100%! 🎉**

---

## 📋 Características Principales

### ✅ **Backend (FastAPI + PostgreSQL)**
- **API REST completa** con CRUD de usuarios y facturas
- **Sistema de validación** de facturas (pendiente → validada/rechazada)
- **Endpoint de visualización** de archivos adjuntos
- **Exportación a Excel** con filtros personalizables
- **Filtros avanzados** por múltiples criterios
- **Dashboard con estadísticas** en tiempo real
- **Pruebas unitarias** completas

### ✅ **Frontend (React + TypeScript)**
- **Dashboard avanzado** con gráficos interactivos y métricas
- **Gestión completa de usuarios** (CRUD con modales)
- **Gestión de facturas** con filtros avanzados
- **Modal de validación** con visualizador de archivos
- **Vista responsive** (tabla/tarjetas para móviles)
- **Diseño profesional** con Tailwind CSS

### ✅ **Funcionalidades Avanzadas**
- **Visualizador de archivos** integrado (PDF, imágenes, Excel)
- **Estadísticas en tiempo real** con gráficos
- **Tendencias mensuales** con insights
- **Ranking de usuarios** por gastos
- **Distribución por categorías** y métodos de pago
- **Métricas de rendimiento** de validación

---

## 🚀 Instalación y Configuración

### **📚 Documentación Completa**

- **[Índice de Documentación](DOCUMENTACION.md)** - Guía completa de toda la documentación disponible
- **[Guía Completa de Instalación](INSTALACION.md)** - Instalación paso a paso del sistema completo
- **[Configuración Gmail API](CONFIGURACION_GMAIL.md)** - Configuración detallada para procesamiento de facturas electrónicas
- **[Configuración OCR](CONFIGURACION_OCR.md)** - Configuración detallada para procesamiento de facturas físicas
- **[Solución de Problemas](TROUBLESHOOTING.md)** - Guía completa para resolver problemas comunes
- **[Despliegue en Producción](DESPLIEGUE_PRODUCCION.md)** - Guía completa para desplegar en producción
- **[Despliegue en GCP](DESPLIEGUE_GCP.md)** - Guía específica para Google Cloud Platform

### **Instalación Rápida**

#### **Prerrequisitos**
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Tesseract OCR

#### **Backend**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install Pillow pytesseract PyMuPDF  # Dependencias OCR

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de PostgreSQL

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### **Frontend**
```bash
cd frontend
npm install
npm run dev
```

#### **Base de Datos**
```sql
-- Crear base de datos
CREATE DATABASE facturas_boosting;

-- Crear usuario
CREATE USER boosting_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE facturas_boosting TO boosting_user;
```

### **Despliegue Rápido con Docker**

```bash
# Clonar repositorio
git clone <repository-url>
cd facturasBst

# Configurar variables de entorno
cp env.example .env
# Editar .env con tus configuraciones

# Desplegar con Docker
./scripts/deploy.sh

# Verificar salud del sistema
./scripts/health-check.sh
```

**Acceso al sistema:**
- **Frontend:** http://localhost
- **Backend API:** http://localhost:8000
- **Documentación API:** http://localhost:8000/docs

### **Despliegue Rápido en Google Cloud Platform**

```bash
# Instalar Google Cloud CLI
curl https://sdk.cloud.google.com | bash

# Autenticar y configurar proyecto
gcloud auth login
gcloud config set project facturasBst

# Desplegar en GCP
./scripts/deploy-gcp.sh

# Verificar despliegue
./scripts/verify-gcp.sh
```

**Acceso al sistema en GCP:**
- **Backend API:** https://facturas-backend-xxxxx-uc.a.run.app
- **Frontend:** https://storage.googleapis.com/facturas-frontend-facturasBst/
- **Documentación API:** https://facturas-backend-xxxxx-uc.a.run.app/docs

---

## 📊 **Estado del Proyecto**

### ✅ **Completado (MVP - Fase 1) - 100% 🎉**
- [x] Configuración del proyecto base
- [x] Modelo de datos (usuarios y facturas)
- [x] API REST completa (CRUD usuarios y facturas)
- [x] Endpoint de carga de facturas con archivos
- [x] Endpoint de consulta con filtros y paginación
- [x] Exportación a Excel
- [x] **Sistema de validación de facturas** (pendiente → validada/rechazada)
- [x] **Gestión completa de usuarios** (CRUD con modales)
- [x] **Filtros avanzados en facturas** (búsqueda, fechas, usuarios, estados)
- [x] **Visualizador de archivos en modal de validación** (PDF, imágenes, Excel)
- [x] **Dashboard avanzado con estadísticas en tiempo real** (gráficos, métricas, tendencias)
- [x] Frontend completo con React + TypeScript
- [x] Modal de validación de facturas
- [x] Pruebas unitarias completas

### 🚀 **Listo para Producción**
- [x] **MVP Fase 1 completado al 100%**
- [x] Sistema funcional y probado
- [x] Documentación completa
- [x] Código en GitHub

### ✅ **Completado (Fase 2) - 100% 🎉**

#### ✅ **Integración con Gmail API - COMPLETADO**
- [x] **Autenticación con Gmail API** (OAuth 2.0)
- [x] **Procesamiento automático de correos** electrónicos
- [x] **Detección automática de facturas** por palabras clave
- [x] **Extracción de datos** (proveedor, monto, fecha, descripción)
- [x] **Creación automática de facturas** en el sistema
- [x] **Estadísticas de Gmail** en tiempo real
- [x] **Dashboard integrado** con funcionalidades de Gmail
- [x] **Tests unitarios** para integración Gmail
- [x] **Documentación de configuración** completa

#### ✅ **OCR para Facturas Físicas - COMPLETADO**
- [x] **Procesamiento OCR** con Tesseract para imágenes y PDFs
- [x] **Extracción automática** de datos (monto, proveedor, fecha, número)
- [x] **Nivel de confianza** para validar la extracción
- [x] **Edición manual** de datos extraídos
- [x] **Creación automática** de facturas desde OCR
- [x] **Interfaz intuitiva** para procesamiento de facturas
- [x] **Soporte múltiples formatos** (JPG, PNG, PDF, TIFF, BMP)
- [x] **Tests unitarios** completos para funcionalidad OCR
- [x] **Componente reactivado** y completamente funcional
- [x] **Patrones de extracción** optimizados para facturas en español

#### ✅ **Sistema de CI/CD - COMPLETADO**
- [x] **GitHub Actions** para CI/CD automático
- [x] **Despliegue automático** a Google Cloud Platform
- [x] **Tests automáticos** y análisis de código
- [x] **Dependabot** para actualización de dependencias
- [x] **Documentación completa** de instalación y despliegue

### 🆕 **Mejoras Recientes (Diciembre 2024)**

#### ✅ **Reactivar Funcionalidad OCR**
- **Problema resuelto:** Componente OCRProcessor desactivado por problemas de TypeScript
- **Soluciones implementadas:**
  - Reactivado componente OCRProcessor en OCRProcessing.tsx
  - Descomentado router Gmail en main.py
  - Arreglados patrones de extracción OCR
  - Mejorada validación de datos extraídos
- **Resultado:** Funcionalidad OCR completamente operativa

### 📋 **Próximas Funcionalidades (Fase 3)**
- [ ] **Procesamiento asíncrono** con Celery
- [ ] **Notificaciones automáticas** por email
- [ ] Autenticación y autorización avanzada
- [ ] Notificaciones push
- [ ] App móvil (React Native)
- [ ] Integración con software contable
- [ ] Análisis predictivo con IA

---

## 🛠 **Tecnologías Utilizadas**

### **Backend**
- **FastAPI** - Framework web moderno y rápido
- **PostgreSQL** - Base de datos relacional
- **SQLAlchemy** - ORM para Python
- **Alembic** - Migraciones de base de datos
- **Pydantic** - Validación de datos
- **pytest** - Framework de testing
- **Tesseract OCR** - Reconocimiento óptico de caracteres
- **PyMuPDF** - Procesamiento de PDFs
- **Pillow** - Procesamiento de imágenes

### **Frontend**
- **React 18** - Biblioteca de UI
- **TypeScript** - JavaScript tipado
- **Vite** - Build tool moderno
- **Tailwind CSS** - Framework de CSS
- **React Query** - Manejo de estado del servidor
- **React Router** - Enrutamiento
- **Lucide React** - Iconos

### **Herramientas**
- **Git** - Control de versiones
- **GitHub** - Repositorio remoto
- **ESLint** - Linter para JavaScript/TypeScript
- **Prettier** - Formateador de código

---

## 📁 **Estructura del Proyecto**

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
│   └── requirements.txt     # Dependencias Python
├── frontend/
│   ├── src/
│   │   ├── components/      # Componentes React
│   │   ├── pages/          # Páginas de la aplicación
│   │   ├── services/       # Cliente API
│   │   └── types/          # Tipos TypeScript
│   └── package.json        # Dependencias Node.js
├── task/                   # Documentación del proyecto
└── README.md              # Este archivo
```

---

## 🧪 **Testing**

### **Backend**
```bash
cd backend
pytest tests/ -v
```

### **Frontend**
```bash
cd frontend
npm test
```

---

## 🔄 **CI/CD Automático**

El proyecto incluye configuración completa de CI/CD con GitHub Actions:

- **CI**: Tests automáticos, linting, análisis de seguridad
- **CD**: Despliegue automático a GCP desde la rama `main`
- **Dependabot**: Actualización automática de dependencias
- **CodeQL**: Análisis estático de código

Ver [CICD_README.md](CICD_README.md) para configuración detallada.

---

## 📚 **Documentación API**

Una vez que el servidor esté ejecutándose, puedes acceder a:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🤝 **Contribución**

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 **Licencia**

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## 👥 **Equipo**

- **Desarrollador Principal**: AlejandroPODropi
- **Cliente**: Boosting
- **Proyecto**: Sistema de Control de Facturas

---

## 📞 **Contacto**

Para preguntas o soporte, contacta al equipo de desarrollo.

---

**¡Sistema de Control de Facturas para Boosting - MVP Fase 1 y Fase 2 Completados! 🎉**