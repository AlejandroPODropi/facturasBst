"""
Modelos de base de datos usando SQLAlchemy.
Define las tablas users e invoices para el sistema de control de facturas.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base
import enum


class UserRole(str, enum.Enum):
    """Roles de usuario en el sistema."""
    COLLABORATOR = "colaborador"
    ACCOUNTING_ASSISTANT = "auxiliar_contable"
    FINANCIAL_MANAGER = "gerencia_financiera"
    ADMIN = "administrador"


class PaymentMethod(str, enum.Enum):
    """Métodos de pago disponibles."""
    CASH = "efectivo"
    TARJETA_BST = "tarjeta_bst"
    TARJETA_PERSONAL = "tarjeta_personal"
    TRANSFER = "transferencia"
    CHECK = "cheque"


class ExpenseCategory(str, enum.Enum):
    """Categorías de gastos."""
    TRANSPORT = "transporte"
    MEALS = "alimentacion"
    ACCOMMODATION = "hospedaje"
    SUPPLIES = "suministros"
    COMMUNICATION = "comunicacion"
    OTHER = "otros"


class InvoiceStatus(str, enum.Enum):
    """Estados de las facturas."""
    PENDING = "pendiente"
    VALIDATED = "validada"
    REJECTED = "rechazada"


class User(Base):
    """Modelo de usuario del sistema."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.COLLABORATOR)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relación con facturas
    invoices = relationship("Invoice", back_populates="user")


class Invoice(Base):
    """Modelo de factura del sistema."""
    
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    provider = Column(String(255), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    category = Column(Enum(ExpenseCategory), nullable=False)
    file_path = Column(String(500), nullable=True)  # Ruta del archivo adjunto
    description = Column(Text, nullable=True)
    nit = Column(String(50), nullable=True, index=True)  # Número de identificación tributaria
    status = Column(Enum(InvoiceStatus), nullable=False, default=InvoiceStatus.PENDING)
    # Campos para OCR
    ocr_data = Column(JSON, nullable=True)  # Datos extraídos por OCR
    ocr_confidence = Column(Float, nullable=True)  # Nivel de confianza del OCR
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relación con usuario
    user = relationship("User", back_populates="invoices")
