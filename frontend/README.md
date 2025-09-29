# 🎨 Frontend - Control de Facturas Boosting

Interfaz de usuario desarrollada con React + TypeScript para el sistema de control de facturas de Boosting.

## 📂 Estructura del Frontend

```
frontend/
├── src/
│   ├── components/        # Componentes reutilizables
│   │   └── Layout.tsx    # Layout principal con navegación
│   ├── pages/            # Páginas de la aplicación
│   │   ├── Dashboard.tsx # Panel principal
│   │   ├── Users.tsx     # Gestión de usuarios
│   │   ├── Invoices.tsx  # Lista de facturas
│   │   └── CreateInvoice.tsx # Crear factura
│   ├── services/         # Servicios de API
│   │   └── api.ts        # Cliente HTTP y endpoints
│   ├── types/            # Tipos TypeScript
│   │   └── index.ts      # Interfaces y enums
│   ├── hooks/            # Custom hooks (futuro)
│   ├── utils/            # Utilidades (futuro)
│   ├── App.tsx           # Componente principal
│   ├── main.tsx          # Punto de entrada
│   └── index.css         # Estilos globales
├── public/               # Archivos estáticos
├── package.json          # Dependencias y scripts
├── tsconfig.json         # Configuración TypeScript
├── vite.config.ts        # Configuración Vite
├── tailwind.config.js    # Configuración Tailwind CSS
└── README.md            # Este archivo
```

## ⚙️ Instalación

### 1. Instalar dependencias

```bash
cd frontend
npm install
```

### 2. Configurar variables de entorno

Crea el archivo `.env.local`:

```bash
VITE_API_URL=http://localhost:8000/api/v1
```

### 3. Ejecutar en modo desarrollo

```bash
npm run dev
```

La aplicación estará disponible en:
- **Frontend:** `http://localhost:3000`

## 🚀 Scripts Disponibles

```bash
# Desarrollo
npm run dev          # Servidor de desarrollo con hot reload

# Construcción
npm run build        # Construir para producción
npm run preview      # Previsualizar build de producción

# Calidad de código
npm run lint         # Ejecutar ESLint
npm run type-check   # Verificar tipos TypeScript
```

## 🎨 Tecnologías

- **React 18** - Biblioteca de UI
- **TypeScript** - Tipado estático
- **Vite** - Build tool y dev server
- **React Router** - Enrutamiento
- **React Query** - Gestión de estado del servidor
- **Axios** - Cliente HTTP
- **Tailwind CSS** - Framework de CSS
- **Lucide React** - Iconos
- **React Hook Form** - Manejo de formularios

## 📱 Características

### ✅ Implementadas
- **Dashboard** con estadísticas generales
- **Gestión completa de usuarios** (CRUD con modales)
- **Gestión de facturas** (listar, crear, exportar)
- **Sistema de validación** de facturas (validar/rechazar)
- **Filtros avanzados** para facturas (búsqueda, fechas, usuarios, estados)
- **Vista responsive** de facturas (tabla/tarjetas)
- **Visualizador de archivos en modal de validación** (PDF, imágenes, Excel)
  - Vista previa integrada de PDFs e imágenes
  - Botón de apertura para archivos Excel/CSV
  - Información completa de la factura en el modal
  - Diseño responsive con dos columnas
- **Formulario de creación** de facturas con validación
- **Modal de validación** con notas opcionales
- **Modales de gestión de usuarios** (crear, editar, eliminar)
- **Navegación** responsive con sidebar
- **Diseño profesional** con Tailwind CSS
- **Tipado completo** con TypeScript

### 🔄 En desarrollo
- Paginación
- Búsqueda en tiempo real
- Notificaciones toast
- Autenticación y autorización

### 🎉 **¡MVP Fase 1 Completado al 100%!**
- Dashboard avanzado con estadísticas en tiempo real
- Gráficos interactivos y métricas
- Sistema completo y funcional

## 🎯 Páginas Disponibles

### Dashboard (`/`)
- Resumen de estadísticas
- Facturas recientes
- Métricas clave del sistema

### Usuarios (`/users`)
- Lista de usuarios del sistema
- **Crear usuarios** con modal dedicado
- **Editar usuarios** con formulario pre-poblado
- **Eliminar usuarios** con confirmación
- Filtros por rol

### Facturas (`/invoices`)
- Lista de facturas con paginación
- **Filtros avanzados** por estado, categoría, usuario, método de pago
- **Búsqueda por texto** en proveedor y descripción
- **Filtros por rango de fechas**
- **Vista responsive** (tabla en desktop, tarjetas en móvil)
- **Tabla optimizada** con columnas responsivas
- **Visualizador de archivos en modal de validación** (PDF, imágenes, Excel)
- Exportación a Excel
- Acciones de edición y eliminación

### Nueva Factura (`/invoices/create`)
- Formulario completo de creación
- Validación en tiempo real
- Subida de archivos adjuntos
- Selección de usuario y categorías

## 🔧 Configuración

### Proxy de API
El frontend está configurado para hacer proxy de las peticiones `/api/*` al backend en `http://localhost:8000`.

### Variables de entorno
- `VITE_API_URL`: URL base de la API (default: `http://localhost:8000/api/v1`)

### Tailwind CSS
Configurado con colores personalizados para el tema de Boosting:
- **Primary:** Azul corporativo
- **Secondary:** Grises neutros
- **Success:** Verde para estados positivos
- **Warning:** Naranja para advertencias
- **Error:** Rojo para errores

## 🚀 Despliegue

### Build de producción
```bash
npm run build
```

Los archivos estáticos se generan en la carpeta `dist/` y pueden ser servidos por cualquier servidor web estático.

### Variables de entorno para producción
```bash
VITE_API_URL=https://api.boosting.com/api/v1
```
