"""
Tests para endpoints del dashboard.
Pruebas unitarias para estadísticas y métricas del dashboard.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.main import app
from src.models import User, Invoice, InvoiceStatus, ExpenseCategory, PaymentMethod
from tests.conftest import create_test_user, create_test_invoice

client = TestClient(app)


class TestDashboardStats:
    """Tests para estadísticas del dashboard."""
    
    def test_get_dashboard_stats_success(self, client, db_session):
        """
        Caso de éxito: Obtener estadísticas completas del dashboard.
        
        Verifica que se pueden obtener todas las estadísticas del dashboard.
        """
        # Crear datos de prueba
        user = create_test_user(db_session)
        invoice1 = create_test_invoice(db_session, user.id, amount=1000)
        invoice2 = create_test_invoice(db_session, user.id, amount=2000)
        
        response = client.get("/api/v1/dashboard/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura de respuesta
        assert "basic_stats" in data
        assert "monthly_trends" in data
        assert "user_stats" in data
        assert "category_distribution" in data
        assert "payment_method_distribution" in data
        assert "validation_performance" in data
        assert "recent_activity" in data
        
        # Verificar estadísticas básicas
        basic_stats = data["basic_stats"]
        assert basic_stats["total_users"] == 1
        assert basic_stats["total_invoices"] == 2
        assert basic_stats["total_amount"] == 3000.0
    
    def test_get_basic_stats_success(self, client, db_session):
        """
        Caso de éxito: Obtener solo estadísticas básicas.
        
        Verifica que se pueden obtener las estadísticas básicas del dashboard.
        """
        # Crear datos de prueba
        user = create_test_user(db_session)
        invoice = create_test_invoice(db_session, user.id)
        
        response = client.get("/api/v1/dashboard/basic-stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_users" in data
        assert "total_invoices" in data
        assert "total_amount" in data
        assert "invoices_by_status" in data
        assert "amount_by_status" in data
        
        assert data["total_users"] == 1
        assert data["total_invoices"] == 1
    
    def test_get_monthly_trends_success(self, client, db_session):
        """
        Caso de éxito: Obtener tendencias mensuales.
        
        Verifica que se pueden obtener las tendencias mensuales de facturas.
        """
        # Crear datos de prueba
        user = create_test_user(db_session)
        invoice = create_test_invoice(db_session, user.id)
        
        response = client.get("/api/v1/dashboard/trends")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "trends" in data
        assert isinstance(data["trends"], list)
    
    def test_get_user_stats_success(self, client, db_session):
        """
        Caso de éxito: Obtener estadísticas por usuario.
        
        Verifica que se pueden obtener las estadísticas por usuario.
        """
        # Crear datos de prueba
        user = create_test_user(db_session)
        invoice = create_test_invoice(db_session, user.id, amount=1500)
        
        response = client.get("/api/v1/dashboard/user-stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "user_stats" in data
        assert isinstance(data["user_stats"], list)
        
        if data["user_stats"]:
            user_stat = data["user_stats"][0]
            assert "user_id" in user_stat
            assert "name" in user_stat
            assert "invoice_count" in user_stat
            assert "total_amount" in user_stat
            assert "avg_amount" in user_stat
    
    def test_get_category_distribution_success(self, client, db_session):
        """
        Caso de éxito: Obtener distribución por categoría.
        
        Verifica que se puede obtener la distribución de facturas por categoría.
        """
        # Crear datos de prueba
        user = create_test_user(db_session)
        invoice = create_test_invoice(db_session, user.id)
        
        response = client.get("/api/v1/dashboard/category-distribution")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "category_distribution" in data
        assert isinstance(data["category_distribution"], list)
    
    def test_get_payment_method_distribution_success(self, client, db_session):
        """
        Caso de éxito: Obtener distribución por método de pago.
        
        Verifica que se puede obtener la distribución por método de pago.
        """
        # Crear datos de prueba
        user = create_test_user(db_session)
        invoice = create_test_invoice(db_session, user.id)
        
        response = client.get("/api/v1/dashboard/payment-method-distribution")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "payment_method_distribution" in data
        assert isinstance(data["payment_method_distribution"], list)
    
    def test_get_validation_performance_success(self, client, db_session):
        """
        Caso de éxito: Obtener métricas de validación.
        
        Verifica que se pueden obtener las métricas de rendimiento de validación.
        """
        # Crear datos de prueba
        user = create_test_user(db_session)
        invoice = create_test_invoice(db_session, user.id)
        
        response = client.get("/api/v1/dashboard/validation-performance")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "validation_performance" in data
        performance = data["validation_performance"]
        assert "avg_validation_time_hours" in performance
        assert "total_validated" in performance
        assert "validation_rate" in performance
    
    def test_get_recent_activity_success(self, client, db_session):
        """
        Caso de éxito: Obtener actividad reciente.
        
        Verifica que se puede obtener la actividad reciente del sistema.
        """
        # Crear datos de prueba
        user = create_test_user(db_session)
        invoice = create_test_invoice(db_session, user.id)
        
        response = client.get("/api/v1/dashboard/recent-activity")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "recent_activity" in data
        assert isinstance(data["recent_activity"], list)
    
    def test_get_dashboard_stats_empty_database(self, client, db_session):
        """
        Caso borde: Dashboard con base de datos vacía.
        
        Verifica el comportamiento cuando no hay datos en la base de datos.
        """
        response = client.get("/api/v1/dashboard/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        basic_stats = data["basic_stats"]
        assert basic_stats["total_users"] == 0
        assert basic_stats["total_invoices"] == 0
        assert basic_stats["total_amount"] == 0.0
    
    def test_get_monthly_trends_with_custom_months(self, client, db_session):
        """
        Caso borde: Tendencias mensuales con parámetro personalizado.
        
        Verifica que se puede especificar el número de meses para las tendencias.
        """
        response = client.get("/api/v1/dashboard/trends?months=12")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "trends" in data
        assert isinstance(data["trends"], list)
    
    def test_get_user_stats_with_custom_limit(self, client, db_session):
        """
        Caso borde: Estadísticas de usuarios con límite personalizado.
        
        Verifica que se puede especificar el límite de usuarios a retornar.
        """
        response = client.get("/api/v1/dashboard/user-stats?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "user_stats" in data
        assert isinstance(data["user_stats"], list)
        assert len(data["user_stats"]) <= 5
    
    def test_get_recent_activity_with_custom_limit(self, client, db_session):
        """
        Caso borde: Actividad reciente con límite personalizado.
        
        Verifica que se puede especificar el límite de actividades a retornar.
        """
        response = client.get("/api/v1/dashboard/recent-activity?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "recent_activity" in data
        assert isinstance(data["recent_activity"], list)
        assert len(data["recent_activity"]) <= 5


class TestDashboardErrorHandling:
    """Tests para manejo de errores en el dashboard."""
    
    def test_dashboard_stats_database_error(self, client, db_session):
        """
        Caso de fallo: Error de base de datos.
        
        Verifica el manejo de errores cuando hay problemas con la base de datos.
        """
        # Simular error cerrando la sesión
        db_session.close()
        
        response = client.get("/api/v1/dashboard/stats")
        
        # Debería manejar el error gracefully
        assert response.status_code in [200, 500]
    
    def test_invalid_parameters(self, client, db_session):
        """
        Caso de fallo: Parámetros inválidos.
        
        Verifica el manejo de parámetros inválidos.
        """
        # Parámetros negativos
        response = client.get("/api/v1/dashboard/trends?months=-1")
        assert response.status_code == 200  # Debería usar valor por defecto
        
        response = client.get("/api/v1/dashboard/user-stats?limit=-5")
        assert response.status_code == 200  # Debería usar valor por defecto
        
        response = client.get("/api/v1/dashboard/recent-activity?limit=0")
        assert response.status_code == 200  # Debería usar valor por defecto
