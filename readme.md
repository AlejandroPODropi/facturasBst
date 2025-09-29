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

### **Prerrequisitos**
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+

### **Backend**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de PostgreSQL

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### **Frontend**
```bash
cd frontend
npm install
npm run dev
```

### **Base de Datos**
```sql
-- Crear base de datos
CREATE DATABASE facturas_boosting;

-- Crear usuario
CREATE USER boosting_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE facturas_boosting TO boosting_user;
```

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
- [x] **Integración con Gmail API** para procesamiento automático de facturas electrónicas
- [x] **OCR para facturas físicas** con Tesseract y patrones de extracción optimizados
- [x] **Dashboard avanzado** con gráficos interactivos y métricas en tiempo real
- [x] **Sistema de CI/CD** con GitHub Actions y despliegue automático a GCP
- [x] **Documentación completa** de instalación, configuración y despliegue

### 📋 **Próximas Funcionalidades (Fase 3)**
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