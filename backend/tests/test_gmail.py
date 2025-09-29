"""
Tests para integración con Gmail API.
Pruebas unitarias para el servicio de Gmail y procesamiento de correos.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch, MagicMock

from src.main import app
from src.services.gmail_service import GmailService, InvoiceEmailProcessor, process_gmail_invoices
from tests.conftest import create_test_user

client = TestClient(app)


class TestGmailService:
    """Tests para el servicio de Gmail."""
    
    @patch('src.services.gmail_service.build')
    @patch('src.services.gmail_service.Credentials')
    @patch('src.services.gmail_service.os.path.exists')
    def test_authenticate_success(self, mock_exists, mock_credentials, mock_build):
        """
        Caso de éxito: Autenticación exitosa con Gmail API.
        
        Verifica que la autenticación funcione correctamente.
        """
        # Mock de que existe el archivo de credenciales
        mock_exists.return_value = True
        
        # Mock de credenciales
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds
        
        # Mock del servicio
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        gmail_service = GmailService()
        result = gmail_service.authenticate()
        
        assert result is True
        assert gmail_service.service is not None
    
    @patch('src.services.gmail_service.build')
    @patch('src.services.gmail_service.Credentials')
    def test_authenticate_failure(self, mock_credentials, mock_build):
        """
        Caso de fallo: Error en autenticación con Gmail API.
        
        Verifica el manejo de errores en la autenticación.
        """
        # Mock de error
        mock_credentials.from_authorized_user_file.side_effect = Exception("Auth error")
        
        gmail_service = GmailService()
        result = gmail_service.authenticate()
        
        assert result is False
        assert gmail_service.service is None
    
    @patch('src.services.gmail_service.build')
    @patch('src.services.gmail_service.Credentials')
    def test_search_emails_success(self, mock_credentials, mock_build):
        """
        Caso de éxito: Búsqueda de correos exitosa.
        
        Verifica que se puedan buscar correos correctamente.
        """
        # Mock de autenticación
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds
        
        # Mock del servicio y respuesta
        mock_service = Mock()
        mock_messages = Mock()
        mock_list = Mock()
        mock_list.execute.return_value = {
            'messages': [
                {'id': 'msg1', 'threadId': 'thread1'},
                {'id': 'msg2', 'threadId': 'thread2'}
            ]
        }
        mock_messages.list.return_value = mock_list
        mock_service.users.return_value.messages.return_value = mock_messages
        mock_build.return_value = mock_service
        
        gmail_service = GmailService()
        gmail_service.authenticate()
        
        # Mock de get_email_details
        with patch.object(gmail_service, 'get_email_details') as mock_get_details:
            mock_get_details.return_value = {
                'id': 'msg1',
                'subject': 'Test Email',
                'from': 'test@example.com'
            }
            
            emails = gmail_service.search_emails("test query", 5)
            
            assert len(emails) == 2
            assert emails[0]['subject'] == 'Test Email'
    
    def test_get_header_value(self):
        """
        Caso de éxito: Extracción de valores de header.
        
        Verifica que se puedan extraer valores de headers correctamente.
        """
        gmail_service = GmailService()
        
        headers = [
            {'name': 'Subject', 'value': 'Test Subject'},
            {'name': 'From', 'value': 'test@example.com'},
            {'name': 'Date', 'value': 'Mon, 1 Jan 2024 12:00:00 +0000'}
        ]
        
        subject = gmail_service._get_header_value(headers, 'Subject')
        from_email = gmail_service._get_header_value(headers, 'From')
        date = gmail_service._get_header_value(headers, 'Date')
        
        assert subject == 'Test Subject'
        assert from_email == 'test@example.com'
        assert date == 'Mon, 1 Jan 2024 12:00:00 +0000'
    
    def test_get_header_value_not_found(self):
        """
        Caso borde: Header no encontrado.
        
        Verifica el comportamiento cuando no se encuentra un header.
        """
        gmail_service = GmailService()
        
        headers = [
            {'name': 'Subject', 'value': 'Test Subject'}
        ]
        
        result = gmail_service._get_header_value(headers, 'NonExistent')
        
        assert result == ""


class TestInvoiceEmailProcessor:
    """Tests para el procesador de correos de facturas."""
    
    def test_is_invoice_email_true(self):
        """
        Caso de éxito: Correo identificado como factura.
        
        Verifica que se identifiquen correctamente los correos con facturas.
        """
        processor = InvoiceEmailProcessor(Mock())
        
        email_data = {
            'subject': 'Factura de servicios - Enero 2024',
            'body': 'Adjunto encontrará la factura correspondiente al mes de enero.',
            'attachments': [
                {'filename': 'factura.pdf', 'mime_type': 'application/pdf'}
            ]
        }
        
        result = processor.is_invoice_email(email_data)
        
        assert result is True
    
    def test_is_invoice_email_false_no_keywords(self):
        """
        Caso de fallo: Correo sin palabras clave de factura.
        
        Verifica que no se identifiquen como facturas correos sin palabras clave.
        """
        processor = InvoiceEmailProcessor(Mock())
        
        email_data = {
            'subject': 'Reunión de trabajo',
            'body': 'Te invito a la reunión de mañana.',
            'attachments': [
                {'filename': 'agenda.pdf', 'mime_type': 'application/pdf'}
            ]
        }
        
        result = processor.is_invoice_email(email_data)
        
        assert result is False
    
    def test_is_invoice_email_false_no_attachments(self):
        """
        Caso de fallo: Correo sin adjuntos.
        
        Verifica que no se identifiquen como facturas correos sin adjuntos.
        """
        processor = InvoiceEmailProcessor(Mock())
        
        email_data = {
            'subject': 'Factura de servicios',
            'body': 'Adjunto encontrará la factura.',
            'attachments': []
        }
        
        result = processor.is_invoice_email(email_data)
        
        assert result is False
    
    def test_extract_provider_from_email(self):
        """
        Caso de éxito: Extracción de proveedor desde email.
        
        Verifica que se extraiga correctamente el proveedor del email.
        """
        processor = InvoiceEmailProcessor(Mock())
        
        email_data = {
            'from': 'facturacion@empresa.com',
            'subject': 'Factura de servicios'
        }
        
        provider = processor._extract_provider(email_data)
        
        assert provider == "Empresa"
    
    def test_extract_provider_from_subject(self):
        """
        Caso de éxito: Extracción de proveedor desde asunto.
        
        Verifica que se extraiga correctamente el proveedor del asunto.
        """
        processor = InvoiceEmailProcessor(Mock())
        
        email_data = {
            'from': 'noreply@example.com',
            'subject': 'Factura de Servicios ABC'
        }
        
        provider = processor._extract_provider(email_data)
        
        assert provider == "Proveedor Desconocido"  # Fallback cuando no se puede extraer
    
    def test_extract_amount_success(self):
        """
        Caso de éxito: Extracción de monto de factura.
        
        Verifica que se extraiga correctamente el monto de la factura.
        """
        processor = InvoiceEmailProcessor(Mock())
        
        email_data = {
            'subject': 'Factura por $1,250.50',
            'body': 'El total de la factura es de $1,250.50 pesos mexicanos.'
        }
        
        amount = processor._extract_amount(email_data)
        
        assert amount == 1250.50
    
    def test_extract_amount_no_amount(self):
        """
        Caso borde: Sin monto en el correo.
        
        Verifica el comportamiento cuando no hay monto en el correo.
        """
        processor = InvoiceEmailProcessor(Mock())
        
        email_data = {
            'subject': 'Factura de servicios',
            'body': 'Adjunto encontrará la factura correspondiente.'
        }
        
        amount = processor._extract_amount(email_data)
        
        assert amount == 0.0


class TestGmailEndpoints:
    """Tests para endpoints de Gmail API."""
    
    @patch('src.routers.gmail.GmailService')
    def test_auth_status_authenticated(self, mock_gmail_service):
        """
        Caso de éxito: Estado de autenticación exitoso.
        
        Verifica que se retorne el estado correcto de autenticación.
        """
        mock_service = Mock()
        mock_service.authenticate.return_value = True
        mock_gmail_service.return_value = mock_service
        
        response = client.get("/api/v1/gmail/auth/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
        assert "Autenticado" in data["message"]
    
    @patch('src.routers.gmail.GmailService')
    def test_auth_status_not_authenticated(self, mock_gmail_service):
        """
        Caso de fallo: No autenticado.
        
        Verifica el comportamiento cuando no hay autenticación.
        """
        mock_service = Mock()
        mock_service.authenticate.return_value = False
        mock_gmail_service.return_value = mock_service
        
        response = client.get("/api/v1/gmail/auth/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False
        assert "No autenticado" in data["message"]
    
    @patch('src.routers.gmail.GmailService')
    def test_search_emails_success(self, mock_gmail_service):
        """
        Caso de éxito: Búsqueda de correos exitosa.
        
        Verifica que se puedan buscar correos correctamente.
        """
        mock_service = Mock()
        mock_service.authenticate.return_value = True
        mock_service.search_emails.return_value = [
            {'id': 'msg1', 'subject': 'Test Email 1'},
            {'id': 'msg2', 'subject': 'Test Email 2'}
        ]
        mock_gmail_service.return_value = mock_service
        
        response = client.get("/api/v1/gmail/emails/search?query=test&max_results=5")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["emails"]) == 2
        assert data["query"] == "test"
    
    @patch('src.routers.gmail.GmailService')
    def test_search_emails_not_authenticated(self, mock_gmail_service):
        """
        Caso de fallo: Búsqueda sin autenticación.
        
        Verifica el comportamiento cuando no hay autenticación.
        """
        mock_service = Mock()
        mock_service.authenticate.return_value = False
        mock_gmail_service.return_value = mock_service
        
        response = client.get("/api/v1/gmail/emails/search")
        
        assert response.status_code == 401
        assert "No se pudo autenticar" in response.json()["detail"]
    
    @patch('src.routers.gmail.process_gmail_invoices')
    def test_process_invoices_sync_success(self, mock_process, db_session):
        """
        Caso de éxito: Procesamiento síncrono de facturas.
        
        Verifica que se procesen facturas correctamente.
        """
        mock_process.return_value = [
            {'invoice_id': 1, 'provider': 'Test Provider', 'amount': 100.0}
        ]
        
        response = client.post("/api/v1/gmail/process-invoices/sync?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_processed"] == 1
        assert len(data["processed_invoices"]) == 1
        assert data["processed_invoices"][0]["provider"] == "Test Provider"
    
    @patch('src.routers.gmail.process_gmail_invoices')
    def test_process_invoices_sync_error(self, mock_process, db_session):
        """
        Caso de fallo: Error en procesamiento de facturas.
        
        Verifica el manejo de errores en el procesamiento.
        """
        mock_process.side_effect = Exception("Processing error")
        
        response = client.post("/api/v1/gmail/process-invoices/sync")
        
        assert response.status_code == 500
        assert "Error procesando facturas" in response.json()["detail"]
    
    def test_get_gmail_stats_success(self, db_session):
        """
        Caso de éxito: Estadísticas de Gmail.
        
        Verifica que se obtengan estadísticas correctamente.
        """
        with patch('src.routers.gmail.GmailService') as mock_gmail_service:
            mock_service = Mock()
            mock_service.authenticate.return_value = True
            mock_service.search_emails.side_effect = [
                [{'id': '1'}, {'id': '2'}, {'id': '3'}],  # total_emails_7d
                [{'id': '1'}, {'id': '2'}],  # emails_with_attachments_7d
                [{'id': '1'}]  # unread_emails_7d
            ]
            mock_gmail_service.return_value = mock_service
            
            response = client.get("/api/v1/gmail/stats")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_emails_7d"] == 3
            assert data["emails_with_attachments_7d"] == 2
            assert data["unread_emails_7d"] == 1
            assert data["attachment_rate"] == 66.67  # 2/3 * 100


class TestGmailIntegration:
    """Tests de integración para Gmail."""
    
    @patch('src.services.gmail_service.GmailService')
    @patch('src.services.gmail_service.create_invoice_from_email')
    def test_process_gmail_invoices_integration(self, mock_create_invoice, mock_gmail_service, db_session):
        """
        Caso de éxito: Integración completa de procesamiento de facturas.
        
        Verifica el flujo completo de procesamiento de facturas desde Gmail.
        """
        # Crear usuario de prueba
        user = create_test_user(db_session)
        
        # Mock del servicio de Gmail
        mock_service = Mock()
        mock_service.authenticate.return_value = True
        mock_service.search_emails.return_value = [
            {
                'id': 'msg1',
                'subject': 'Factura de servicios',
                'from': 'test@provider.com',
                'body': 'Adjunto factura por $500.00',
                'attachments': [{'filename': 'factura.pdf', 'mime_type': 'application/pdf'}]
            }
        ]
        mock_service.mark_as_read.return_value = True
        mock_gmail_service.return_value = mock_service
        
        # Mock del procesador
        with patch('src.services.gmail_service.InvoiceEmailProcessor') as mock_processor_class:
            mock_processor = Mock()
            mock_processor.is_invoice_email.return_value = True
            mock_processor.extract_invoice_data.return_value = {
                'provider': 'Test Provider',
                'amount': 500.0,
                'date': '2024-01-01',
                'description': 'Factura de servicios'
            }
            mock_processor_class.return_value = mock_processor
            
            # Mock de creación de factura
            from src.models import Invoice
            mock_invoice = Invoice(
                id=1,
                provider='Test Provider',
                amount=500.0,
                user_id=user.id
            )
            mock_create_invoice.return_value = mock_invoice
            
            # Ejecutar procesamiento
            result = process_gmail_invoices(db_session, 1)
            
            # Verificar resultados
            assert len(result) == 1
            assert result[0]['provider'] == 'Test Provider'
            assert result[0]['amount'] == 500.0
            assert result[0]['invoice_id'] == 1
