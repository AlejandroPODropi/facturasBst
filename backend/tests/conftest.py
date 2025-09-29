"""
Configuración de pytest para las pruebas unitarias.
Define fixtures comunes para testing.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database import get_db, Base
from src.models import User, Invoice, UserRole, PaymentMethod, ExpenseCategory, InvoiceStatus

# Base de datos de prueba en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override de la dependencia de base de datos para testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Cliente de prueba para la API."""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user():
    """Usuario de prueba."""
    return {
        "name": "Juan Pérez",
        "email": "juan.perez@boosting.com",
        "role": UserRole.COLLABORATOR
    }


@pytest.fixture
def test_invoice():
    """Factura de prueba."""
    return {
        "date": "2024-01-15T10:30:00",
        "provider": "Restaurante El Buen Sabor",
        "amount": 25.50,
        "payment_method": PaymentMethod.CARD,
        "category": ExpenseCategory.MEALS,
        "description": "Almuerzo de trabajo"
    }


@pytest.fixture
def created_user(client, test_user):
    """Usuario creado en la base de datos de prueba."""
    response = client.post("/api/v1/users/", json=test_user)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def created_invoice(client, created_user, test_invoice):
    """Factura creada en la base de datos de prueba."""
    invoice_data = {**test_invoice, "user_id": created_user["id"]}
    response = client.post("/api/v1/invoices/upload", data=invoice_data)
    assert response.status_code == 201
    return response.json()
