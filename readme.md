📑 Control de Facturas – Boosting

## 🚀 Propósito

Sistema interno para **registrar, validar y consolidar facturas** de colaboradores de Boosting.
El objetivo es reducir errores operativos, optimizar la carga contable y garantizar que todos los gastos queden soportados para su deducción tributaria.

---

## 📂 Estructura del proyecto

```
facturasBst/
├── backend/      # API REST (FastAPI + PostgreSQL)
│   ├── src/      # Código fuente del backend
│   ├── tests/    # Pruebas unitarias
│   ├── alembic/  # Migraciones de BD
│   └── README.md # Documentación del backend
├── frontend/     # Interfaz web (React + TypeScript)
│   ├── src/      # Código fuente del frontend
│   ├── public/   # Archivos estáticos
│   └── README.md # Documentación del frontend
├── task/         # PLANNING.md y TASK.md
├── .env          # Variables de entorno
└── README.md     # Este archivo
```

---

## ⚙️ Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/boosting/control-facturas.git
cd control-facturas
```

### 2. Configurar Backend

```bash
cd backend

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos PostgreSQL
createdb facturas_boosting

# Crear tablas
python3 -c "from src.database import engine, Base; from src.models import User, Invoice; Base.metadata.create_all(bind=engine)"
```

### 3. Configurar Frontend

```bash
cd ../frontend

# Instalar dependencias
npm install

# Crear archivo de variables de entorno
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env.local
```

### 4. Variables de entorno

El archivo `.env` ya está configurado en la raíz del proyecto con:
- Configuración de PostgreSQL
- Claves de autenticación
- Configuración de archivos

---

## ▶️ Ejecución

### 1. Iniciar Backend

```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --reload
```

**Backend disponible en:**
- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 2. Iniciar Frontend

```bash
cd frontend
npm run dev
```

**Frontend disponible en:**
- Aplicación web: `http://localhost:3000`

### 3. Acceder a la aplicación

1. Abre `http://localhost:3000` en tu navegador
2. Explora el dashboard con estadísticas
3. Gestiona usuarios y facturas desde la interfaz web
4. Prueba la creación de facturas con archivos adjuntos

---

## 🧪 Pruebas

Ejecutar todos los tests:

```bash
pytest tests/
```

Ejecutar tests con cobertura:

```bash
pytest tests/ --cov=src --cov-report=html
```

Los tests cubren:
- **Casos de éxito**: Funcionalidad normal de la API
- **Casos de borde**: Valores límite y condiciones especiales
- **Casos de fallo**: Manejo de errores y validaciones

---

## 🌍 Variables de entorno

Definidas en `.env.example`:

* `DB_URL`: conexión a la base de datos PostgreSQL.
* `SECRET_KEY`: clave para tokens JWT.
* `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USER`, `EMAIL_PASSWORD`: configuración de correo (fase 2).
* `OCR_API_KEY`: clave para servicio OCR (fase 2).
* `ENV`, `DEBUG`: configuración del entorno.

---

## 📌 Roadmap inicial

* **Fase 1:** Registro manual de facturas y exportación a Excel.
* **Fase 2:** Integración correo + OCR + dashboard.
* **Fase 3:** Clasificación automática de gastos + integración contable.

---

## 🚀 Estado del Proyecto

### ✅ Completado (MVP - Fase 1)
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
- [x] Frontend completo con React + TypeScript
- [x] Dashboard con estadísticas
- [x] Modal de validación de facturas
- [x] Pruebas unitarias completas

### 🔄 En Desarrollo
- [ ] Mejoras en el Dashboard (gráficos, métricas)

### 📋 Próximas Funcionalidades
- [ ] Integración con correo electrónico
- [ ] OCR para facturas físicas
- [ ] Dashboard avanzado con gráficos
- [ ] Clasificación automática de gastos
- [ ] Integración con software contable

---

## 👨‍💻 Buenas prácticas

* Archivos < 500 líneas.
* Código modular y documentado con docstrings.
* Pruebas unitarias por funcionalidad (éxito, borde, fallo).
* Actualizar siempre `README.md` y `TASK.md` tras cada cambio.

