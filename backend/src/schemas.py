"""
Esquemas Pydantic para validación de datos.
Define los modelos de entrada y salida para la API.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from src.models import UserRole, PaymentMethod, ExpenseCategory, InvoiceStatus


# Esquemas de Usuario
class UserBase(BaseModel):
    """Esquema base para usuario."""
    name: str = Field(..., min_length=2, max_length=100, description="Nombre completo del usuario")
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    role: UserRole = Field(default=UserRole.COLLABORATOR, description="Rol del usuario en el sistema")


class UserCreate(UserBase):
    """Esquema para crear un nuevo usuario."""
    pass


class UserUpdate(BaseModel):
    """Esquema para actualizar un usuario existente."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None


class User(UserBase):
    """Esquema de respuesta para usuario."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Esquemas de Factura
class InvoiceBase(BaseModel):
    """Esquema base para factura."""
    date: datetime = Field(..., description="Fecha de la factura")
    provider: str = Field(..., min_length=2, max_length=255, description="Nombre del proveedor")
    amount: float = Field(..., gt=0, description="Monto de la factura (debe ser mayor a 0)")
    payment_method: PaymentMethod = Field(..., description="Método de pago utilizado")
    category: ExpenseCategory = Field(..., description="Categoría del gasto")
    description: Optional[str] = Field(None, max_length=1000, description="Descripción adicional")
    nit: Optional[str] = Field(None, max_length=50, description="Número de identificación tributaria")


class InvoiceCreate(InvoiceBase):
    """Esquema para crear una nueva factura."""
    user_id: int = Field(..., description="ID del usuario que registra la factura")


class InvoiceUpdate(BaseModel):
    """Esquema para actualizar una factura existente."""
    date: Optional[datetime] = None
    provider: Optional[str] = Field(None, min_length=2, max_length=255)
    amount: Optional[float] = Field(None, gt=0)
    payment_method: Optional[PaymentMethod] = None
    category: Optional[ExpenseCategory] = None
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[InvoiceStatus] = None


class Invoice(InvoiceBase):
    """Esquema de respuesta para factura."""
    id: int
    user_id: int
    file_path: Optional[str] = None
    status: InvoiceStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: User
    
    class Config:
        from_attributes = True


class InvoiceWithFile(Invoice):
    """Esquema de factura con información de archivo."""
    file_url: Optional[str] = None


# Esquemas para consultas y filtros
class InvoiceFilters(BaseModel):
    """Esquema para filtros de consulta de facturas."""
    user_id: Optional[int] = None
    status: Optional[InvoiceStatus] = None
    category: Optional[ExpenseCategory] = None
    payment_method: Optional[PaymentMethod] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    provider: Optional[str] = None
    search_text: Optional[str] = Field(None, description="Búsqueda por texto en proveedor o descripción")


class PaginationParams(BaseModel):
    """Esquema para parámetros de paginación."""
    page: int = Field(default=1, ge=1, description="Número de página")
    size: int = Field(default=10, ge=1, le=100, description="Tamaño de página")


class PaginatedResponse(BaseModel):
    """Esquema para respuestas paginadas."""
    items: List[Invoice]
    total: int
    page: int
    size: int
    pages: int


# Esquemas para exportación
class ExportParams(BaseModel):
    """Esquema para parámetros de exportación."""
    user_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[InvoiceStatus] = None
    format: str = Field(default="excel", pattern="^(excel|csv)$")


# Esquemas de respuesta de la API
class MessageResponse(BaseModel):
    """Esquema para respuestas de mensaje."""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Esquema para respuestas de error."""
    message: str
    detail: Optional[str] = None
    success: bool = False
