"""
Punto de entrada principal de la aplicación FastAPI.
Control de Facturas Boosting - Sistema de registro y consolidación de facturas.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from src.routers import invoices, users, dashboard
from src.database import engine
from src.models import Base

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Crear directorio de uploads si no existe
os.makedirs("uploads", exist_ok=True)

app = FastAPI(
    title="Control de Facturas Boosting",
    description="Sistema de registro, validación y consolidación de facturas para colaboradores de Boosting",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Incluir routers
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(invoices.router, prefix="/api/v1/invoices", tags=["invoices"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["dashboard"])


@app.get("/")
async def root():
    """
    Endpoint raíz de la API.
    
    Returns:
        dict: Mensaje de bienvenida y información básica de la API
    """
    return {
        "message": "Control de Facturas Boosting API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """
    Endpoint de verificación de salud de la API.
    
    Returns:
        dict: Estado de la aplicación
    """
    return {"status": "healthy", "service": "control-facturas-boosting"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
