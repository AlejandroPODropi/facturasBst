"""
Configuración de la base de datos PostgreSQL.
Maneja la conexión y sesión de SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
from google.cloud.sql.connector import Connector

# Cargar variables de entorno
load_dotenv()


class Settings(BaseSettings):
    """Configuración de la aplicación desde variables de entorno."""
    
    database_url: str = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/facturas_boosting")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    upload_dir: str = os.getenv("UPLOAD_DIR", "./uploads")
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignorar campos adicionales en el .env


settings = Settings()

# Función para crear conexión con Cloud SQL
def getconn():
    """Crear conexión a Cloud SQL usando el connector."""
    connector = Connector()
    
    # Extraer información de la URL de conexión
    if "host=/cloudsql/" in settings.database_url:
        # Formato: postgresql://user:pass@/db?host=/cloudsql/project:region:instance
        import re
        match = re.search(r'postgresql://([^:]+):([^@]+)@/([^?]+)\?host=(.+)', settings.database_url)
        if match:
            user, password, db_name, host = match.groups()
            # El host debe ser solo la parte después de /cloudsql/
            instance_connection_name = host.replace('/cloudsql/', '')
            conn = connector.connect(
                instance_connection_name,
                "pg8000",
                user=user,
                password=password,
                db=db_name,
            )
            return conn
    
    # Fallback para conexiones locales o IP directa
    return None

# Crear engine de SQLAlchemy
# Usar conexión directa (local o IP) por ahora
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=settings.debug
)

# Crear sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos declarativos
Base = declarative_base()


def get_db():
    """
    Dependency para obtener sesión de base de datos.
    
    Yields:
        Session: Sesión de SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
