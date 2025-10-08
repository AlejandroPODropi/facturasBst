# Sistema de Gestión de Facturas - FacturasBST

## 🚀 Estado del Proyecto: **COMPLETAMENTE OPERATIVO**

Sistema completo de gestión de facturas con integración Gmail, procesamiento OCR y análisis automático de facturas colombianas.

## 📋 Características Principales

### ✅ Funcionalidades Implementadas

- **🔐 Sistema de Usuarios:** Autenticación, roles y gestión de perfiles
- **📄 Gestión de Facturas:** Carga manual, edición, eliminación y visualización
- **📧 Integración Gmail:** Análisis automático de emails y procesamiento en lote
- **🤖 Procesamiento OCR:** Extracción automática de datos de PDFs e imágenes
- **📊 Dashboard:** Estadísticas, gráficos y métricas en tiempo real
- **📱 Diseño Responsivo:** Optimizado para desktop y móviles
- **🔍 Búsqueda y Filtros:** Búsqueda avanzada y filtros múltiples
- **📈 Reportes:** Visualización de tendencias y estadísticas

### 🎯 Casos de Uso Principales

1. **Carga Manual de Facturas**
   - Subida de archivos PDF/imágenes
   - Procesamiento OCR automático
   - Revisión y confirmación de datos

2. **Procesamiento Automático desde Gmail**
   - Análisis de emails en busca de facturas
   - Detección automática de patrones colombianos
   - Procesamiento en lote con asignación de usuarios

3. **Gestión y Consulta**
   - Visualización con paginación
   - Filtros por usuario, proveedor, fecha, estado
   - Edición y eliminación de facturas

## 🛠️ Tecnologías Utilizadas

### Backend
- **FastAPI** - Framework web moderno y rápido
- **PostgreSQL** - Base de datos relacional
- **SQLAlchemy** - ORM para Python
- **Alembic** - Migraciones de base de datos
- **Google Cloud SQL** - Base de datos en la nube
- **Tesseract OCR** - Procesamiento de imágenes
- **Gmail API** - Integración con Gmail
- **Google Secret Manager** - Gestión de credenciales

### Frontend
- **React 18** - Biblioteca de interfaz de usuario
- **TypeScript** - JavaScript con tipos estáticos
- **Tailwind CSS** - Framework de CSS utilitario
- **React Query** - Gestión de estado del servidor
- **React Router** - Enrutamiento del lado del cliente
- **Lucide React** - Iconos modernos

### Infraestructura
- **Google Cloud Run** - Contenedores serverless
- **Docker** - Contenedorización
- **Google Cloud Storage** - Almacenamiento de archivos
- **Google Cloud Logging** - Logs centralizados

## 🚀 URLs del Sistema

### Producción
- **Frontend:** [https://frontend-493189429371.us-central1.run.app](https://frontend-493189429371.us-central1.run.app)
- **Backend:** [https://backend-493189429371.us-central1.run.app](https://backend-493189429371.us-central1.run.app)

### Documentación API
- **Swagger UI:** [https://backend-493189429371.us-central1.run.app/docs](https://backend-493189429371.us-central1.run.app/docs)
- **ReDoc:** [https://backend-493189429371.us-central1.run.app/redoc](https://backend-493189429371.us-central1.run.app/redoc)

## 📊 Métodos de Pago y Categorías

### Métodos de Pago
- **Tarjeta BST** - Tarjeta corporativa
- **Tarjeta Personal** - Tarjeta personal del empleado
- **Efectivo** - Pago en efectivo
- **Transferencia** - Transferencia bancaria

### Categorías de Gastos
- **Alimentación** - Gastos de comida y bebida
- **Transporte** - Gastos de movilidad
- **Servicios** - Servicios públicos y profesionales
- **Suministros** - Materiales y suministros
- **Mantenimiento** - Gastos de mantenimiento
- **Otros** - Gastos diversos

## 🔧 Configuración del Entorno

### Requisitos
- Node.js 18+
- Python 3.12+
- Docker
- Google Cloud CLI

### Variables de Entorno

#### Backend
```bash
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-secret-key
DEBUG=false
```

#### Frontend
```bash
VITE_API_URL=https://backend-493189429371.us-central1.run.app
```

## 🚀 Instalación y Despliegue

### Desarrollo Local

1. **Clonar el repositorio:**
```bash
git clone <repository-url>
cd facturasBst
```

2. **Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

3. **Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Despliegue en Producción

1. **Construir imágenes Docker:**
```bash
# Backend
cd backend
docker build --platform linux/amd64 -t us-central1-docker.pkg.dev/facturasbst/facturas-repo/backend:latest .

# Frontend
cd frontend
docker build --platform linux/amd64 -t us-central1-docker.pkg.dev/facturasbst/facturas-repo/frontend:latest .
```

2. **Subir al registro:**
```bash
docker push us-central1-docker.pkg.dev/facturasbst/facturas-repo/backend:latest
docker push us-central1-docker.pkg.dev/facturasbst/facturas-repo/frontend:latest
```

3. **Desplegar en Cloud Run:**
```bash
# Backend
gcloud run deploy backend \
  --image us-central1-docker.pkg.dev/facturasbst/facturas-repo/backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 900 \
  --concurrency 10 \
  --max-instances 10

# Frontend
gcloud run deploy frontend \
  --image us-central1-docker.pkg.dev/facturasbst/facturas-repo/frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 3000 \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --concurrency 10 \
  --max-instances 5
```

## 📁 Estructura del Proyecto

```
facturasBst/
├── backend/
│   ├── src/
│   │   ├── main.py              # Punto de entrada de la aplicación
│   │   ├── database.py          # Configuración de base de datos
│   │   ├── models.py            # Modelos SQLAlchemy
│   │   ├── schemas.py           # Esquemas Pydantic
│   │   ├── routers/             # Endpoints de la API
│   │   │   ├── auth.py          # Autenticación
│   │   │   ├── users.py         # Gestión de usuarios
│   │   │   ├── invoices.py      # Gestión de facturas
│   │   │   ├── dashboard.py     # Dashboard y estadísticas
│   │   │   ├── gmail.py         # Integración Gmail
│   │   │   └── ocr.py           # Procesamiento OCR
│   │   └── services/            # Lógica de negocio
│   │       ├── auth_service.py  # Servicios de autenticación
│   │       ├── user_service.py  # Servicios de usuario
│   │       ├── invoice_service.py # Servicios de facturas
│   │       ├── dashboard_service.py # Servicios de dashboard
│   │       ├── gmail_service.py # Servicios de Gmail
│   │       └── ocr_service.py   # Servicios de OCR
│   ├── alembic/                 # Migraciones de base de datos
│   ├── requirements.txt         # Dependencias Python
│   └── Dockerfile              # Imagen Docker del backend
├── frontend/
│   ├── src/
│   │   ├── components/          # Componentes React
│   │   │   ├── Dashboard.tsx    # Componente del dashboard
│   │   │   ├── InvoiceList.tsx  # Lista de facturas
│   │   │   ├── CreateInvoice.tsx # Crear factura
│   │   │   ├── EditInvoiceModal.tsx # Editar factura
│   │   │   ├── DeleteInvoiceModal.tsx # Eliminar factura
│   │   │   ├── InvoiceAnalysis.tsx # Análisis de facturas Gmail
│   │   │   └── GmailIntegration.tsx # Integración Gmail
│   │   ├── pages/               # Páginas de la aplicación
│   │   │   ├── Dashboard.tsx    # Página del dashboard
│   │   │   ├── Invoices.tsx     # Página de facturas
│   │   │   └── Users.tsx        # Página de usuarios
│   │   ├── services/            # Servicios de API
│   │   │   └── api.ts           # Cliente de API
│   │   ├── types/               # Tipos TypeScript
│   │   │   └── index.ts         # Definiciones de tipos
│   │   ├── App.tsx              # Componente principal
│   │   └── main.tsx             # Punto de entrada
│   ├── package.json             # Dependencias Node.js
│   └── Dockerfile              # Imagen Docker del frontend
└── documentos/                  # Documentación del proyecto
    ├── README_ACTUALIZADO.md    # Este archivo
    ├── GUIA_USUARIO_FINAL.md    # Guía de usuario
    ├── RESUMEN_ESTADO_ACTUAL_SISTEMA.md # Estado actual
    └── SOLUCION_COMPLETA_PROCESAMIENTO_LOTE.md # Solución de problemas
```

## 🔍 API Endpoints Principales

### Autenticación
- `POST /api/v1/auth/login` - Iniciar sesión
- `POST /api/v1/auth/register` - Registro de usuario
- `POST /api/v1/auth/refresh` - Renovar token

### Usuarios
- `GET /api/v1/users/` - Listar usuarios
- `POST /api/v1/users/` - Crear usuario
- `GET /api/v1/users/{id}` - Obtener usuario
- `PUT /api/v1/users/{id}` - Actualizar usuario
- `DELETE /api/v1/users/{id}` - Eliminar usuario

### Facturas
- `GET /api/v1/invoices/` - Listar facturas
- `POST /api/v1/invoices/` - Crear factura
- `GET /api/v1/invoices/{id}` - Obtener factura
- `PUT /api/v1/invoices/{id}` - Actualizar factura
- `DELETE /api/v1/invoices/{id}` - Eliminar factura
- `POST /api/v1/invoices/bulk-create` - Crear facturas en lote

### Dashboard
- `GET /api/v1/dashboard/stats` - Estadísticas generales
- `GET /api/v1/dashboard/user-stats` - Estadísticas por usuario
- `GET /api/v1/dashboard/invoice-trends` - Tendencias de facturas

### Gmail
- `GET /api/v1/gmail/auth/status` - Estado de autenticación
- `GET /api/v1/gmail/auth/url` - URL de autorización
- `POST /api/v1/gmail/auth/callback` - Callback de autorización
- `GET /api/v1/gmail/emails/search` - Buscar emails
- `GET /api/v1/gmail/analyze-invoices` - Analizar facturas
- `GET /api/v1/gmail/stats` - Estadísticas de Gmail

### OCR
- `POST /api/v1/ocr/process` - Procesar archivo con OCR

## 🧪 Pruebas

### Backend
```bash
cd backend
pytest tests/
```

### Frontend
```bash
cd frontend
npm test
```

## 📈 Métricas y Monitoreo

### Rendimiento
- **Tiempo de respuesta del backend:** < 2 segundos
- **Carga de páginas del frontend:** < 3 segundos
- **Procesamiento OCR:** < 10 segundos por factura
- **Análisis de emails Gmail:** < 30 segundos por lote

### Disponibilidad
- **Uptime del backend:** 99.9%
- **Uptime del frontend:** 99.9%
- **Conectividad de base de datos:** Estable

## 🔒 Seguridad

- **Autenticación JWT** con tokens seguros
- **Validación de datos** en frontend y backend
- **CORS configurado** correctamente
- **Credenciales almacenadas** en Google Secret Manager
- **Conexiones HTTPS** en producción
- **Validación de archivos** en uploads

## 📚 Documentación Adicional

- **[Guía de Usuario](documentos/GUIA_USUARIO_FINAL.md)** - Manual completo para usuarios finales
- **[Estado Actual del Sistema](documentos/RESUMEN_ESTADO_ACTUAL_SISTEMA.md)** - Resumen técnico del estado
- **[Solución de Problemas](documentos/SOLUCION_COMPLETA_PROCESAMIENTO_LOTE.md)** - Solución de problemas comunes

## 🤝 Contribución

### Flujo de Trabajo
1. Fork del repositorio
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### Estándares de Código
- **Backend:** PEP 8, Black formatter, Flake8 linter
- **Frontend:** ESLint, Prettier, TypeScript strict mode
- **Commits:** Conventional Commits
- **Documentación:** Markdown con ejemplos

## 📞 Soporte

### Problemas Comunes
1. **Error de conexión:** Verificar variables de entorno
2. **OCR no funciona:** Verificar calidad de imagen
3. **Gmail no conecta:** Verificar autorización OAuth

### Contacto
- **Issues:** Usar el sistema de issues de GitHub
- **Documentación:** Revisar la documentación en `/documentos`
- **Logs:** Verificar logs en Google Cloud Logging

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🎯 Roadmap

### Próximas Funcionalidades
- [ ] Exportación de reportes a Excel/PDF
- [ ] Notificaciones por email
- [ ] Integración con más proveedores de email
- [ ] Dashboard avanzado con más métricas
- [ ] API para integraciones externas
- [ ] Aplicación móvil nativa

### Optimizaciones
- [ ] Cache de consultas frecuentes
- [ ] Compresión de imágenes
- [ ] Optimización de consultas SQL
- [ ] Implementación de CDN

---

**Versión:** 2.0  
**Última actualización:** 5 de octubre de 2025  
**Estado:** ✅ **COMPLETAMENTE OPERATIVO**  
**Desarrollado por:** Equipo de Desarrollo FacturasBST