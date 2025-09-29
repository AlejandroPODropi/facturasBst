# 🚀 Backend - Control de Facturas Boosting

API REST desarrollada con FastAPI para el sistema de control de facturas de Boosting.

## 📂 Estructura del Backend

```
backend/
├── src/                    # Código fuente de la API
│   ├── main.py            # Punto de entrada FastAPI
│   ├── database.py        # Configuración PostgreSQL
│   ├── models.py          # Modelos SQLAlchemy
│   ├── schemas.py         # Esquemas Pydantic
│   ├── routers/           # Endpoints de la API
│   │   ├── users.py       # CRUD usuarios
│   │   └── invoices.py    # CRUD facturas + exportación
│   └── services/          # Lógica de negocio
│       └── excel_export.py # Exportación a Excel
├── tests/                 # Pruebas unitarias
│   ├── conftest.py        # Configuración pytest
│   ├── test_users.py      # Tests usuarios
│   └── test_invoices.py   # Tests facturas
├── alembic/               # Migraciones de BD
├── requirements.txt       # Dependencias Python
├── pytest.ini           # Configuración testing
├── alembic.ini          # Configuración migraciones
└── README.md            # Este archivo
```

## ⚙️ Instalación

### 1. Crear entorno virtual

```bash
cd backend
python3 -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crea el archivo `.env` en la raíz del proyecto:

```bash
# Configuración de la base de datos
DB_URL=postgresql://facturas_user:facturas_password@localhost:5432/facturas_boosting

# Configuración de autenticación
SECRET_KEY=your-secret-key-here-change-in-production-boosting-2024
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuración del entorno
ENV=development
DEBUG=True

# Configuración de almacenamiento de archivos
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB en bytes
```

### 4. Configurar base de datos

```bash
# Crear tablas
python3 -c "from src.database import engine, Base; from src.models import User, Invoice; Base.metadata.create_all(bind=engine)"
```

## ▶️ Ejecución

### Modo desarrollo

```bash
uvicorn src.main:app --reload
```

La API estará disponible en:
- **API:** `http://127.0.0.1:8000`
- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

## 🧪 Pruebas

```bash
# Ejecutar todos los tests
pytest tests/

# Ejecutar con cobertura
pytest tests/ --cov=src --cov-report=html
```

## 📋 Endpoints Disponibles

### Usuarios
- `POST /api/v1/users/` - Crear usuario
- `GET /api/v1/users/` - Listar usuarios (paginado)
- `GET /api/v1/users/{id}` - Obtener usuario
- `PUT /api/v1/users/{id}` - Actualizar usuario
- `DELETE /api/v1/users/{id}` - Eliminar usuario

### Facturas
- `POST /api/v1/invoices/upload` - Registrar factura
- `GET /api/v1/invoices/` - Listar facturas (filtros + paginación)
- `GET /api/v1/invoices/{id}` - Obtener factura
- `PUT /api/v1/invoices/{id}` - Actualizar factura
- `PATCH /api/v1/invoices/{id}/validate` - Validar/rechazar factura
- `DELETE /api/v1/invoices/{id}` - Eliminar factura
- `GET /api/v1/invoices/export/excel` - Exportar a Excel

## 🗄️ Base de Datos

### Modelos
- **User:** Usuarios del sistema (colaboradores, auxiliares, gerencia)
- **Invoice:** Facturas registradas por los usuarios

### Enums
- **UserRole:** colaborador, auxiliar_contable, gerencia_financiera, administrador
- **PaymentMethod:** efectivo, tarjeta, transferencia, cheque
- **ExpenseCategory:** transporte, alimentacion, hospedaje, suministros, comunicacion, otros
- **InvoiceStatus:** pendiente, validada, rechazada

## 🔧 Tecnologías

- **FastAPI** - Framework web moderno y rápido
- **PostgreSQL** - Base de datos relacional
- **SQLAlchemy** - ORM para Python
- **Pydantic** - Validación de datos
- **Alembic** - Migraciones de base de datos
- **pytest** - Framework de testing
- **openpyxl** - Exportación a Excel
