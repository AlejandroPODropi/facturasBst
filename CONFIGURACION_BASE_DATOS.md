# Configuración de Base de Datos - Facturas Boosting

## 🏗️ Arquitectura de Base de Datos

### Entornos
- **Desarrollo Local**: PostgreSQL local con `psycopg2`
- **Producción**: Cloud SQL PostgreSQL con Cloud SQL Connector (`pg8000`)

### Instancia de Cloud SQL
- **Nombre**: `facturas-db`
- **Región**: `us-central1`
- **Proyecto**: `facturasbst`
- **Base de datos**: `facturas_boosting`
- **Usuario**: `boosting_user`

## 🔧 Configuración de Conexión

### Variables de Entorno

#### Desarrollo Local
```bash
DATABASE_URL=postgresql://boosting_user:boosting_password_2024@localhost:5432/facturas_boosting
```

#### Producción (Cloud Run)
```bash
DATABASE_URL=postgresql://boosting_user:boosting_password_2024@/facturas_boosting?host=/cloudsql/facturasbst:us-central1:facturas-db
```

### Configuración del Engine SQLAlchemy

```python
# backend/src/database.py
from sqlalchemy import create_engine
from google.cloud.sql.connector import Connector

def getconn():
    """Crear conexión a Cloud SQL usando el connector."""
    connector = Connector()
    
    if "host=/cloudsql/" in settings.database_url:
        import re
        match = re.search(r'postgresql://([^:]+):([^@]+)@/([^?]+)\?host=(.+)', settings.database_url)
        if match:
            user, password, db_name, host = match.groups()
            instance_connection_name = host.replace('/cloudsql/', '')
            conn = connector.connect(
                instance_connection_name,
                "pg8000",
                user=user,
                password=password,
                db=db_name,
            )
            return conn
    
    return None

# Crear engine de SQLAlchemy
if "host=/cloudsql/" in settings.database_url:
    engine = create_engine(
        "postgresql+pg8000://",
        creator=getconn,
        pool_pre_ping=True,
        echo=settings.debug
    )
else:
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        echo=settings.debug
    )
```

## 📊 Estructura de Base de Datos

### Tabla: `users`
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'colaborador',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Tabla: `invoices`
```sql
CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    date TIMESTAMP NOT NULL,
    provider VARCHAR(255) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    file_path VARCHAR(500),
    description TEXT,
    nit VARCHAR(20),
    status VARCHAR(50) DEFAULT 'pendiente',
    ocr_data JSONB,
    ocr_confidence DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Índices
```sql
-- Índice para búsquedas por NIT
CREATE INDEX idx_invoices_nit ON invoices(nit);

-- Índice para búsquedas por usuario
CREATE INDEX idx_invoices_user_id ON invoices(user_id);

-- Índice para búsquedas por fecha
CREATE INDEX idx_invoices_date ON invoices(date);

-- Índice para búsquedas por proveedor
CREATE INDEX idx_invoices_provider ON invoices(provider);
```

## 🔄 Migraciones con Alembic

### Configuración de Alembic
```ini
# alembic.ini
sqlalchemy.url = postgresql://boosting_user:boosting_password_2024@localhost:5432/facturas_boosting
```

### Comandos de Migración

#### Desarrollo Local
```bash
cd backend
source venv/bin/activate
export DATABASE_URL="postgresql://boosting_user:boosting_password_2024@localhost:5432/facturas_boosting"
alembic upgrade head
```

#### Producción
```bash
cd backend
source venv/bin/activate
export DATABASE_URL="postgresql://boosting_user:boosting_password_2024@/facturas_boosting?host=/cloudsql/facturasbst:us-central1:facturas-db"
alembic upgrade head
```

### Migraciones Existentes

#### 0001_add_ocr_fields_to_invoices.py
```python
"""Add OCR fields to invoices

Revision ID: 0001_add_ocr_fields_to_invoices
Revises: 
Create Date: 2025-09-30 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('invoices', sa.Column('ocr_data', sa.JSON(), nullable=True))
    op.add_column('invoices', sa.Column('ocr_confidence', sa.DECIMAL(precision=3, scale=2), nullable=True))

def downgrade():
    op.drop_column('invoices', 'ocr_confidence')
    op.drop_column('invoices', 'ocr_data')
```

#### 0002_add_nit_field_to_invoices.py
```python
"""Add NIT field to invoices

Revision ID: 0002_add_nit_field_to_invoices
Revises: 0001_add_ocr_fields_to_invoices
Create Date: 2025-09-30 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('invoices', sa.Column('nit', sa.VARCHAR(length=20), nullable=True))
    op.create_index('idx_invoices_nit', 'invoices', ['nit'])

def downgrade():
    op.drop_index('idx_invoices_nit', table_name='invoices')
    op.drop_column('invoices', 'nit')
```

## 🔐 Seguridad y Permisos

### Usuario de Base de Datos
```sql
-- Crear usuario
CREATE USER boosting_user WITH PASSWORD 'boosting_password_2024';

-- Otorgar permisos
GRANT ALL PRIVILEGES ON DATABASE facturas_boosting TO boosting_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO boosting_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO boosting_user;
```

### Configuración de Cloud SQL
- **Autorización de redes**: Solo IPs autorizadas
- **SSL**: Habilitado por defecto
- **Backup automático**: Habilitado
- **Alta disponibilidad**: Configurada

## 📈 Monitoreo y Mantenimiento

### Comandos de Monitoreo
```bash
# Estado de la instancia
gcloud sql instances describe facturas-db

# Operaciones recientes
gcloud sql operations list --instance=facturas-db

# Usuarios
gcloud sql users list --instance=facturas-db

# Bases de datos
gcloud sql databases list --instance=facturas-db
```

### Métricas Importantes
- **Conexiones activas**: Monitorear límites
- **Uso de CPU**: Optimizar consultas si es necesario
- **Uso de memoria**: Ajustar configuración si es necesario
- **Espacio en disco**: Monitorear crecimiento

## 🚨 Troubleshooting

### Problemas Comunes

#### Error: "column does not exist"
```bash
# Verificar estructura de tabla
gcloud sql connect facturas-db --user=boosting_user --database=facturas_boosting
\dt invoices
\d invoices
```

#### Error: "connection refused"
```bash
# Verificar estado de la instancia
gcloud sql instances describe facturas-db

# Verificar autorización de IP
gcloud sql instances describe facturas-db --format="value(settings.ipConfiguration.authorizedNetworks[].value)"
```

#### Error: "authentication failed"
```bash
# Verificar credenciales
gcloud sql users list --instance=facturas-db

# Cambiar contraseña si es necesario
gcloud sql users set-password boosting_user --instance=facturas-db --password=nueva_password
```

### Logs de Debugging
```bash
# Logs del backend
gcloud run services logs read backend --region=us-central1 --limit=100

# Logs de Cloud SQL
gcloud logging read "resource.type=cloudsql_database" --limit=50
```

## 🔄 Backup y Recuperación

### Backup Automático
- **Frecuencia**: Diaria
- **Retención**: 7 días
- **Horario**: 02:00 UTC

### Backup Manual
```bash
# Crear backup manual
gcloud sql backups create --instance=facturas-db --description="Backup manual $(date)"
```

### Restauración
```bash
# Listar backups disponibles
gcloud sql backups list --instance=facturas-db

# Restaurar desde backup
gcloud sql backups restore BACKUP_ID --restore-instance=facturas-db
```

## 📋 Checklist de Despliegue

### Antes del Despliegue
- [ ] Verificar que las migraciones estén actualizadas
- [ ] Probar conexión local
- [ ] Verificar variables de entorno
- [ ] Revisar permisos de usuario

### Después del Despliegue
- [ ] Verificar health check
- [ ] Probar endpoint de facturas
- [ ] Verificar logs de conexión
- [ ] Monitorear métricas de base de datos

---

**Última actualización**: 30 de Septiembre de 2025  
**Versión**: 1.0  
**Mantenido por**: Equipo de Desarrollo
