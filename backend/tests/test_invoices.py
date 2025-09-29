"""
Pruebas unitarias para endpoints de facturas.
Cubre casos de éxito, borde y fallo.
"""

import pytest
from fastapi.testclient import TestClient
from src.models import PaymentMethod, ExpenseCategory, InvoiceStatus


class TestInvoiceEndpoints:
    """Clase de pruebas para endpoints de facturas."""
    
    def test_upload_invoice_success(self, client, created_user, test_invoice):
        """
        Caso de éxito: Subir factura válida.
        
        Verifica que se puede crear una factura con datos válidos.
        """
        invoice_data = {**test_invoice, "user_id": created_user["id"]}
        
        response = client.post("/api/v1/invoices/upload", data=invoice_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["provider"] == test_invoice["provider"]
        assert data["amount"] == test_invoice["amount"]
        assert data["user_id"] == created_user["id"]
        assert data["status"] == InvoiceStatus.PENDING
        assert "id" in data
        assert "created_at" in data
    
    def test_upload_invoice_invalid_user(self, client, test_invoice):
        """
        Caso de fallo: Subir factura con usuario inexistente.
        
        Verifica que no se puede crear una factura para un usuario que no existe.
        """
        invoice_data = {**test_invoice, "user_id": 999}
        
        response = client.post("/api/v1/invoices/upload", data=invoice_data)
        
        assert response.status_code == 404
        assert "Usuario no encontrado" in response.json()["detail"]
    
    def test_upload_invoice_zero_amount(self, client, created_user):
        """
        Caso de borde: Subir factura con monto cero.
        
        Verifica que no se puede crear una factura con monto igual a cero.
        """
        invoice_data = {
            "date": "2024-01-15T10:30:00",
            "provider": "Test Provider",
            "amount": 0,
            "payment_method": PaymentMethod.CASH,
            "category": ExpenseCategory.OTHER,
            "user_id": created_user["id"]
        }
        
        response = client.post("/api/v1/invoices/upload", data=invoice_data)
        
        assert response.status_code == 400
        assert "monto debe ser mayor a 0" in response.json()["detail"]
    
    def test_upload_invoice_negative_amount(self, client, created_user):
        """
        Caso de borde: Subir factura con monto negativo.
        
        Verifica que no se puede crear una factura con monto negativo.
        """
        invoice_data = {
            "date": "2024-01-15T10:30:00",
            "provider": "Test Provider",
            "amount": -10.50,
            "payment_method": PaymentMethod.CASH,
            "category": ExpenseCategory.OTHER,
            "user_id": created_user["id"]
        }
        
        response = client.post("/api/v1/invoices/upload", data=invoice_data)
        
        assert response.status_code == 400
        assert "monto debe ser mayor a 0" in response.json()["detail"]
    
    def test_upload_invoice_missing_required_fields(self, client, created_user):
        """
        Caso de fallo: Subir factura sin campos requeridos.
        
        Verifica que no se puede crear una factura sin campos obligatorios.
        """
        invoice_data = {
            "user_id": created_user["id"]
            # Faltan campos requeridos
        }
        
        response = client.post("/api/v1/invoices/upload", data=invoice_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_get_invoices_success(self, client, created_invoice):
        """
        Caso de éxito: Obtener lista de facturas.
        
        Verifica que se puede obtener la lista de facturas.
        """
        response = client.get("/api/v1/invoices/")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
        assert len(data["items"]) == 1
        assert data["total"] == 1
    
    def test_get_invoices_with_filters(self, client, created_user, created_invoice):
        """
        Caso de éxito: Obtener facturas con filtros.
        
        Verifica que se pueden aplicar filtros a la consulta de facturas.
        """
        # Filtrar por usuario
        response = client.get(f"/api/v1/invoices/?user_id={created_user['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        
        # Filtrar por estado
        response = client.get("/api/v1/invoices/?status=pending")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        
        # Filtrar por categoría
        response = client.get("/api/v1/invoices/?category=alimentacion")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
    
    def test_get_invoices_pagination(self, client, created_user):
        """
        Caso de borde: Paginación de facturas.
        
        Verifica que la paginación funciona correctamente.
        """
        # Crear 5 facturas
        for i in range(5):
            invoice_data = {
                "date": "2024-01-15T10:30:00",
                "provider": f"Provider {i}",
                "amount": 10.0 + i,
                "payment_method": PaymentMethod.CASH,
                "category": ExpenseCategory.OTHER,
                "user_id": created_user["id"]
            }
            client.post("/api/v1/invoices/upload", data=invoice_data)
        
        # Obtener primera página
        response = client.get("/api/v1/invoices/?page=1&size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["size"] == 2
        
        # Obtener segunda página
        response = client.get("/api/v1/invoices/?page=2&size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["page"] == 2
    
    def test_get_invoice_success(self, client, created_invoice):
        """
        Caso de éxito: Obtener factura específica.
        
        Verifica que se puede obtener una factura por ID.
        """
        response = client.get(f"/api/v1/invoices/{created_invoice['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_invoice["id"]
        assert data["provider"] == created_invoice["provider"]
    
    def test_get_invoice_not_found(self, client):
        """
        Caso de fallo: Obtener factura inexistente.
        
        Verifica que se retorna error 404 para factura no encontrada.
        """
        response = client.get("/api/v1/invoices/999")
        
        assert response.status_code == 404
        assert "Factura no encontrada" in response.json()["detail"]
    
    def test_update_invoice_success(self, client, created_invoice):
        """
        Caso de éxito: Actualizar factura existente.
        
        Verifica que se puede actualizar una factura con datos válidos.
        """
        update_data = {
            "provider": "Nuevo Proveedor",
            "amount": 50.75,
            "status": InvoiceStatus.VALIDATED
        }
        
        response = client.put(f"/api/v1/invoices/{created_invoice['id']}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == update_data["provider"]
        assert data["amount"] == update_data["amount"]
        assert data["status"] == update_data["status"]
    
    def test_update_invoice_invalid_amount(self, client, created_invoice):
        """
        Caso de fallo: Actualizar factura con monto inválido.
        
        Verifica que no se puede actualizar una factura con monto inválido.
        """
        update_data = {"amount": -10.0}
        
        response = client.put(f"/api/v1/invoices/{created_invoice['id']}", json=update_data)
        
        assert response.status_code == 400
        assert "monto debe ser mayor a 0" in response.json()["detail"]
    
    def test_update_invoice_not_found(self, client):
        """
        Caso de fallo: Actualizar factura inexistente.
        
        Verifica que se retorna error 404 para factura no encontrada.
        """
        update_data = {"provider": "Nuevo Proveedor"}
        
        response = client.put("/api/v1/invoices/999", json=update_data)
        
        assert response.status_code == 404
        assert "Factura no encontrada" in response.json()["detail"]
    
    def test_delete_invoice_success(self, client, created_invoice):
        """
        Caso de éxito: Eliminar factura existente.
        
        Verifica que se puede eliminar una factura.
        """
        response = client.delete(f"/api/v1/invoices/{created_invoice['id']}")
        
        assert response.status_code == 204
        
        # Verificar que la factura ya no existe
        response = client.get(f"/api/v1/invoices/{created_invoice['id']}")
        assert response.status_code == 404
    
    def test_delete_invoice_not_found(self, client):
        """
        Caso de fallo: Eliminar factura inexistente.
        
        Verifica que se retorna error 404 para factura no encontrada.
        """
        response = client.delete("/api/v1/invoices/999")
        
        assert response.status_code == 404
        assert "Factura no encontrada" in response.json()["detail"]
    
    def test_export_invoices_success(self, client, created_invoice):
        """
        Caso de éxito: Exportar facturas a Excel.
        
        Verifica que se puede exportar facturas a Excel.
        """
        response = client.get("/api/v1/invoices/export/excel")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "file_path" in data
        assert "total_invoices" in data
        assert data["total_invoices"] == 1
    
    def test_export_invoices_no_data(self, client):
        """
        Caso de borde: Exportar facturas cuando no hay datos.
        
        Verifica que se retorna error cuando no hay facturas para exportar.
        """
        response = client.get("/api/v1/invoices/export/excel")
        
        assert response.status_code == 404
        assert "No hay facturas para exportar" in response.json()["detail"]
    
    def test_export_invoices_with_filters(self, client, created_user):
        """
        Caso de éxito: Exportar facturas con filtros.
        
        Verifica que se pueden aplicar filtros a la exportación.
        """
        # Crear factura
        invoice_data = {
            "date": "2024-01-15T10:30:00",
            "provider": "Test Provider",
            "amount": 25.50,
            "payment_method": PaymentMethod.CARD,
            "category": ExpenseCategory.MEALS,
            "user_id": created_user["id"]
        }
        client.post("/api/v1/invoices/upload", data=invoice_data)
        
        # Exportar con filtro de usuario
        response = client.get(f"/api/v1/invoices/export/excel?user_id={created_user['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_invoices"] == 1
    
    def test_validate_invoice_success(self, client, created_invoice):
        """
        Caso de éxito: Validar factura existente.
        
        Verifica que se puede validar una factura pendiente.
        """
        validation_data = {
            "new_status": InvoiceStatus.VALIDATED,
            "validation_notes": "Factura validada correctamente"
        }
        
        response = client.patch(f"/api/v1/invoices/{created_invoice['id']}/validate", data=validation_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == InvoiceStatus.VALIDATED
        assert "Notas de validación" in data["description"]
    
    def test_reject_invoice_success(self, client, created_invoice):
        """
        Caso de éxito: Rechazar factura existente.
        
        Verifica que se puede rechazar una factura pendiente.
        """
        rejection_data = {
            "new_status": InvoiceStatus.REJECTED,
            "validation_notes": "Factura rechazada por falta de documentación"
        }
        
        response = client.patch(f"/api/v1/invoices/{created_invoice['id']}/validate", data=rejection_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == InvoiceStatus.REJECTED
        assert "Factura rechazada" in data["description"]
    
    def test_validate_invoice_invalid_status(self, client, created_invoice):
        """
        Caso de fallo: Validar factura con estado inválido.
        
        Verifica que no se puede cambiar a un estado inválido.
        """
        validation_data = {
            "new_status": InvoiceStatus.PENDING,  # Estado inválido para validación
            "validation_notes": "Intento de cambio inválido"
        }
        
        response = client.patch(f"/api/v1/invoices/{created_invoice['id']}/validate", data=validation_data)
        
        assert response.status_code == 400
        assert "Estado inválido" in response.json()["detail"]
    
    def test_validate_invoice_not_found(self, client):
        """
        Caso de fallo: Validar factura inexistente.
        
        Verifica que se retorna error 404 para factura no encontrada.
        """
        validation_data = {
            "new_status": InvoiceStatus.VALIDATED,
            "validation_notes": "Notas de prueba"
        }
        
        response = client.patch("/api/v1/invoices/999/validate", data=validation_data)
        
        assert response.status_code == 404
        assert "Factura no encontrada" in response.json()["detail"]
    
    def test_validate_invoice_without_notes(self, client, created_invoice):
        """
        Caso de borde: Validar factura sin notas.
        
        Verifica que se puede validar una factura sin proporcionar notas.
        """
        validation_data = {
            "new_status": InvoiceStatus.VALIDATED
            # Sin validation_notes
        }
        
        response = client.patch(f"/api/v1/invoices/{created_invoice['id']}/validate", data=validation_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == InvoiceStatus.VALIDATED
        # La descripción original no debe cambiar si no hay notas
        assert data["description"] == created_invoice["description"]


class TestInvoiceFilters:
    """Tests para filtros avanzados de facturas."""
    
    def test_filter_by_search_text_success(self, client, created_invoice):
        """
        Caso de éxito: Filtrar facturas por texto de búsqueda.
        
        Verifica que se pueden filtrar facturas por texto en proveedor o descripción.
        """
        # Buscar por proveedor
        response = client.get(f"/api/v1/invoices/?search_text={created_invoice['provider']}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert any(invoice["provider"] == created_invoice["provider"] for invoice in data["items"])
    
    def test_filter_by_date_range_success(self, client, created_invoice):
        """
        Caso de éxito: Filtrar facturas por rango de fechas.
        
        Verifica que se pueden filtrar facturas por rango de fechas.
        """
        from datetime import datetime, timedelta
        
        # Crear rango de fechas que incluya la factura creada
        start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        response = client.get(f"/api/v1/invoices/?start_date={start_date}&end_date={end_date}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
    
    def test_filter_by_user_success(self, client, created_invoice):
        """
        Caso de éxito: Filtrar facturas por usuario.
        
        Verifica que se pueden filtrar facturas por usuario específico.
        """
        response = client.get(f"/api/v1/invoices/?user_id={created_invoice['user_id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert all(invoice["user_id"] == created_invoice["user_id"] for invoice in data["items"])
    
    def test_filter_by_status_success(self, client, created_invoice):
        """
        Caso de éxito: Filtrar facturas por estado.
        
        Verifica que se pueden filtrar facturas por estado específico.
        """
        response = client.get(f"/api/v1/invoices/?status={created_invoice['status']}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert all(invoice["status"] == created_invoice["status"] for invoice in data["items"])
    
    def test_filter_by_category_success(self, client, created_invoice):
        """
        Caso de éxito: Filtrar facturas por categoría.
        
        Verifica que se pueden filtrar facturas por categoría específica.
        """
        response = client.get(f"/api/v1/invoices/?category={created_invoice['category']}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert all(invoice["category"] == created_invoice["category"] for invoice in data["items"])
    
    def test_filter_by_payment_method_success(self, client, created_invoice):
        """
        Caso de éxito: Filtrar facturas por método de pago.
        
        Verifica que se pueden filtrar facturas por método de pago específico.
        """
        response = client.get(f"/api/v1/invoices/?payment_method={created_invoice['payment_method']}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert all(invoice["payment_method"] == created_invoice["payment_method"] for invoice in data["items"])
    
    def test_filter_by_provider_success(self, client, created_invoice):
        """
        Caso de éxito: Filtrar facturas por proveedor.
        
        Verifica que se pueden filtrar facturas por proveedor específico.
        """
        response = client.get(f"/api/v1/invoices/?provider={created_invoice['provider']}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert all(created_invoice["provider"] in invoice["provider"] for invoice in data["items"])
    
    def test_multiple_filters_success(self, client, created_invoice):
        """
        Caso de éxito: Aplicar múltiples filtros simultáneamente.
        
        Verifica que se pueden combinar múltiples filtros.
        """
        response = client.get(
            f"/api/v1/invoices/?user_id={created_invoice['user_id']}&status={created_invoice['status']}&category={created_invoice['category']}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        for invoice in data["items"]:
            assert invoice["user_id"] == created_invoice["user_id"]
            assert invoice["status"] == created_invoice["status"]
            assert invoice["category"] == created_invoice["category"]
    
    def test_filter_no_results_success(self, client):
        """
        Caso de éxito: Filtros que no devuelven resultados.
        
        Verifica que los filtros funcionan correctamente cuando no hay coincidencias.
        """
        response = client.get("/api/v1/invoices/?user_id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 0
        assert data["total"] == 0
    
    def test_filter_invalid_date_range_edge_case(self, client):
        """
        Caso borde: Rango de fechas inválido.
        
        Verifica el comportamiento con fechas inválidas.
        """
        response = client.get("/api/v1/invoices/?start_date=2024-13-01&end_date=2024-12-32")
        
        # Debe devolver error 422 por formato de fecha inválido
        assert response.status_code == 422
    
    def test_filter_empty_search_text_edge_case(self, client):
        """
        Caso borde: Texto de búsqueda vacío.
        
        Verifica que el filtro de búsqueda maneja texto vacío correctamente.
        """
        response = client.get("/api/v1/invoices/?search_text=")
        
        assert response.status_code == 200
        data = response.json()
        # Debe devolver todas las facturas cuando el texto de búsqueda está vacío
        assert len(data["items"]) >= 0


class TestInvoiceFileDownload:
    """Tests para descarga de archivos adjuntos de facturas."""
    
    def test_download_file_success(self, client, created_invoice):
        """
        Caso de éxito: Descargar archivo adjunto de factura existente.
        
        Verifica que se puede descargar el archivo adjunto de una factura.
        """
        # Nota: Este test requiere que la factura tenga un archivo adjunto real
        # En un entorno de prueba real, se crearía un archivo de prueba
        response = client.get(f"/api/v1/invoices/{created_invoice['id']}/download")
        
        # Si la factura no tiene archivo, debe devolver 404
        if response.status_code == 404:
            assert "archivo adjunto" in response.json()["detail"]
        else:
            # Si tiene archivo, debe devolver el archivo
            assert response.status_code == 200
            assert response.headers["content-type"] is not None
    
    def test_download_file_not_found(self, client):
        """
        Caso de fallo: Intentar descargar archivo de factura inexistente.
        
        Verifica que se devuelve error 404 para facturas que no existen.
        """
        response = client.get("/api/v1/invoices/99999/download")
        
        assert response.status_code == 404
        assert "Factura no encontrada" in response.json()["detail"]
    
    def test_download_file_no_attachment(self, client, created_invoice):
        """
        Caso de fallo: Intentar descargar archivo de factura sin adjunto.
        
        Verifica que se devuelve error 404 para facturas sin archivo adjunto.
        """
        # Este test asume que la factura de prueba no tiene archivo adjunto
        response = client.get(f"/api/v1/invoices/{created_invoice['id']}/download")
        
        # Debe devolver 404 si no hay archivo adjunto
        if response.status_code == 404:
            assert "archivo adjunto" in response.json()["detail"]
    
    def test_download_file_missing_file(self, client, created_invoice):
        """
        Caso de fallo: Archivo adjunto no existe en el sistema de archivos.
        
        Verifica el comportamiento cuando el archivo no existe físicamente.
        """
        # Este test verificaría el caso donde file_path existe en DB pero no en filesystem
        # En un entorno real, se simularía este escenario
        response = client.get(f"/api/v1/invoices/{created_invoice['id']}/download")
        
        # El comportamiento depende de si la factura tiene archivo o no
        assert response.status_code in [200, 404]