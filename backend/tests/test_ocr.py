"""
Tests unitarios para el servicio OCR.
Prueba la funcionalidad de extracción de texto y datos de facturas.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import io

from src.services.ocr_service import OCRService, ocr_service


class TestOCRService:
    """Tests para el servicio OCR."""
    
    def setup_method(self):
        """Configurar el servicio OCR para cada test."""
        self.ocr_service = OCRService()
    
    def test_is_supported_format_success(self):
        """Test: Verificar formatos soportados - caso éxito."""
        # Casos de éxito
        assert self.ocr_service.is_supported_format("factura.jpg") == True
        assert self.ocr_service.is_supported_format("factura.jpeg") == True
        assert self.ocr_service.is_supported_format("factura.png") == True
        assert self.ocr_service.is_supported_format("factura.pdf") == True
        assert self.ocr_service.is_supported_format("factura.tiff") == True
        assert self.ocr_service.is_supported_format("factura.bmp") == True
    
    def test_is_supported_format_failure(self):
        """Test: Verificar formatos no soportados - caso fallo."""
        # Casos de fallo
        assert self.ocr_service.is_supported_format("factura.txt") == False
        assert self.ocr_service.is_supported_format("factura.doc") == False
        assert self.ocr_service.is_supported_format("factura.docx") == False
        assert self.ocr_service.is_supported_format("factura") == False
    
    def test_extract_amount_success(self):
        """Test: Extraer monto de factura - caso éxito."""
        test_cases = [
            ("total: $1,500.00", 1500.0),
            ("monto: 2,500.50", 2500.5),
            ("importe: 3,000", 3000.0),
            ("valor: $500.25", 500.25),
            ("$1,200.75", 1200.75),
            ("1500.00 pesos", 1500.0),
        ]
        
        for text, expected_amount in test_cases:
            result = self.ocr_service._extract_amount(text.lower())
            assert result == expected_amount, f"Failed for text: {text}"
    
    def test_extract_amount_failure(self):
        """Test: Extraer monto de factura - caso fallo."""
        test_cases = [
            "sin monto visible",
            "total: $0.00",
            "monto: -100",
            "importe: abc",
        ]
        
        for text in test_cases:
            result = self.ocr_service._extract_amount(text.lower())
            assert result is None, f"Should return None for text: {text}"
    
    def test_extract_provider_success(self):
        """Test: Extraer proveedor de factura - caso éxito."""
        test_cases = [
            ("proveedor: Supermercado ABC", "Supermercado Abc"),
            ("vendedor: Tienda XYZ", "Tienda Xyz"),
            ("empresa: Restaurante 123", "Restaurante 123"),
            ("razón social: Farmacia Central", "Farmacia Central"),
        ]
        
        for text, expected_provider in test_cases:
            result = self.ocr_service._extract_provider(text.lower())
            assert result == expected_provider, f"Failed for text: {text}"
    
    def test_extract_provider_failure(self):
        """Test: Extraer proveedor de factura - caso fallo."""
        test_cases = [
            "sin proveedor visible",
            "proveedor: AB",  # Muy corto
            "vendedor: ",  # Vacío
        ]
        
        for text in test_cases:
            result = self.ocr_service._extract_provider(text.lower())
            assert result is None, f"Should return None for text: {text}"
    
    def test_extract_date_success(self):
        """Test: Extraer fecha de factura - caso éxito."""
        test_cases = [
            ("fecha: 15/01/2024", "2024-01-15T00:00:00"),
            ("emisión: 2024-01-15", "2024-01-15T00:00:00"),
            ("15/01/24", "2024-01-15T00:00:00"),
            ("2024-01-15", "2024-01-15T00:00:00"),
        ]
        
        for text, expected_date in test_cases:
            result = self.ocr_service._extract_date(text.lower())
            assert result == expected_date, f"Failed for text: {text}"
    
    def test_extract_date_failure(self):
        """Test: Extraer fecha de factura - caso fallo."""
        test_cases = [
            "sin fecha visible",
            "fecha: 32/13/2024",  # Fecha inválida
            "emisión: abc",  # No es fecha
        ]
        
        for text in test_cases:
            result = self.ocr_service._extract_date(text.lower())
            assert result is None, f"Should return None for text: {text}"
    
    def test_extract_invoice_number_success(self):
        """Test: Extraer número de factura - caso éxito."""
        test_cases = [
            ("factura n°: 12345", "12345"),
            ("no factura: 67890", "67890"),
            ("comprobante n°: ABC-123", "ABC-123"),
        ]
        
        for text, expected_number in test_cases:
            result = self.ocr_service._extract_invoice_number(text.lower())
            assert result == expected_number, f"Failed for text: {text}"
    
    def test_extract_invoice_number_failure(self):
        """Test: Extraer número de factura - caso fallo."""
        test_cases = [
            "sin número de factura",
            "factura n°: ",  # Vacío
        ]
        
        for text in test_cases:
            result = self.ocr_service._extract_invoice_number(text.lower())
            assert result is None, f"Should return None for text: {text}"
    
    def test_calculate_confidence_success(self):
        """Test: Calcular confianza de extracción - caso éxito."""
        # Caso con todos los datos
        data_all = {
            'amount': 1500.0,
            'provider': 'Supermercado ABC',
            'date': '2024-01-15',
            'invoice_number': '12345'
        }
        confidence = self.ocr_service._calculate_confidence(data_all)
        assert confidence == 1.0
        
        # Caso con solo monto
        data_amount_only = {
            'amount': 1500.0,
            'provider': None,
            'date': None,
            'invoice_number': None
        }
        confidence = self.ocr_service._calculate_confidence(data_amount_only)
        assert confidence == 0.4
        
        # Caso con monto y proveedor
        data_amount_provider = {
            'amount': 1500.0,
            'provider': 'Supermercado ABC',
            'date': None,
            'invoice_number': None
        }
        confidence = self.ocr_service._calculate_confidence(data_amount_provider)
        assert confidence == 0.7
    
    def test_extract_invoice_data_success(self):
        """Test: Extraer datos completos de factura - caso éxito."""
        text = """
        FACTURA
        Proveedor: Supermercado ABC
        Fecha: 15/01/2024
        Factura N°: 12345
        Total: $1,500.00
        """
        
        result = self.ocr_service.extract_invoice_data(text)
        
        assert result['amount'] == 1500.0
        assert result['provider'] == 'Supermercado Abc'
        assert result['date'] == '2024-01-15T00:00:00'
        assert result['invoice_number'] == '12345'
        assert result['confidence'] > 0.8
        assert 'raw_text' in result
    
    def test_extract_invoice_data_partial(self):
        """Test: Extraer datos parciales de factura - caso borde."""
        text = """
        FACTURA
        Total: $1,500.00
        """
        
        result = self.ocr_service.extract_invoice_data(text)
        
        assert result['amount'] == 1500.0
        assert result['provider'] is None
        assert result['date'] is None
        assert result['invoice_number'] is None
        assert result['confidence'] == 0.4
    
    def test_extract_invoice_data_failure(self):
        """Test: Extraer datos de factura sin información - caso fallo."""
        text = "texto sin información de factura"
        
        result = self.ocr_service.extract_invoice_data(text)
        
        assert result['amount'] is None
        assert result['provider'] is None
        assert result['date'] is None
        assert result['invoice_number'] is None
        assert result['confidence'] == 0.0
    
    @patch('pytesseract.image_to_string')
    def test_extract_text_from_image_success(self, mock_tesseract):
        """Test: Extraer texto de imagen - caso éxito."""
        # Mock de Tesseract
        mock_tesseract.return_value = "FACTURA\nTotal: $1,500.00"
        
        # Crear imagen temporal
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            # Crear una imagen simple
            img = Image.new('RGB', (100, 100), color='white')
            img.save(temp_file.name, 'JPEG')
            
            try:
                result = self.ocr_service.extract_text_from_image(temp_file.name)
                assert result == "FACTURA\nTotal: $1,500.00"
                mock_tesseract.assert_called_once()
            finally:
                os.unlink(temp_file.name)
    
    @patch('pytesseract.image_to_string')
    def test_extract_text_from_image_failure(self, mock_tesseract):
        """Test: Extraer texto de imagen - caso fallo."""
        # Mock de Tesseract que lanza excepción
        mock_tesseract.side_effect = Exception("OCR Error")
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            img = Image.new('RGB', (100, 100), color='white')
            img.save(temp_file.name, 'JPEG')
            
            try:
                with pytest.raises(Exception, match="OCR Error"):
                    self.ocr_service.extract_text_from_image(temp_file.name)
            finally:
                os.unlink(temp_file.name)
    
    def test_extract_text_from_file_unsupported_format(self):
        """Test: Extraer texto de archivo no soportado - caso fallo."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_file.flush()
            
            try:
                with pytest.raises(ValueError, match="Formato de archivo no soportado"):
                    self.ocr_service.extract_text_from_file(temp_file.name)
            finally:
                os.unlink(temp_file.name)
    
    def test_extract_text_from_file_not_found(self):
        """Test: Extraer texto de archivo inexistente - caso fallo."""
        with pytest.raises(FileNotFoundError):
            self.ocr_service.extract_text_from_file("archivo_inexistente.jpg")
    
    @patch('src.services.ocr_service.ocr_service.extract_text_from_file')
    @patch('src.services.ocr_service.ocr_service.extract_invoice_data')
    def test_process_invoice_file_success(self, mock_extract_data, mock_extract_text):
        """Test: Procesar archivo de factura completo - caso éxito."""
        # Mocks
        mock_extract_text.return_value = "FACTURA\nTotal: $1,500.00"
        mock_extract_data.return_value = {
            'amount': 1500.0,
            'provider': 'Supermercado ABC',
            'date': '2024-01-15',
            'invoice_number': '12345',
            'confidence': 0.9,
            'raw_text': "FACTURA\nTotal: $1,500.00"
        }
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_file.write(b"fake image content")
            temp_file.flush()
            
            try:
                result = self.ocr_service.process_invoice_file(temp_file.name)
                
                assert result['amount'] == 1500.0
                assert result['provider'] == 'Supermercado ABC'
                assert result['confidence'] == 0.9
                assert 'file_path' in result
                assert 'file_size' in result
                assert 'processed_at' in result
                assert 'text_length' in result
                
                mock_extract_text.assert_called_once_with(temp_file.name)
                mock_extract_data.assert_called_once_with("FACTURA\nTotal: $1,500.00")
                
            finally:
                os.unlink(temp_file.name)
    
    def test_process_invoice_file_unsupported_format(self):
        """Test: Procesar archivo no soportado - caso fallo."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_file.flush()
            
            try:
                with pytest.raises(ValueError, match="Formato de archivo no soportado"):
                    self.ocr_service.process_invoice_file(temp_file.name)
            finally:
                os.unlink(temp_file.name)
    
    @patch('src.services.ocr_service.ocr_service.extract_text_from_file')
    def test_process_invoice_file_empty_text(self, mock_extract_text):
        """Test: Procesar archivo sin texto - caso fallo."""
        # Mock que retorna texto vacío
        mock_extract_text.return_value = ""
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_file.write(b"fake image content")
            temp_file.flush()
            
            try:
                with pytest.raises(ValueError, match="No se pudo extraer texto del archivo"):
                    self.ocr_service.process_invoice_file(temp_file.name)
            finally:
                os.unlink(temp_file.name)


class TestOCRServiceIntegration:
    """Tests de integración para el servicio OCR."""
    
    def test_ocr_service_singleton(self):
        """Test: Verificar que ocr_service es una instancia singleton."""
        from src.services.ocr_service import ocr_service
        assert isinstance(ocr_service, OCRService)
        assert ocr_service is not None
    
    def test_patterns_configuration(self):
        """Test: Verificar configuración de patrones regex."""
        service = OCRService()
        
        # Verificar que los patrones están definidos
        assert 'amount' in service.patterns
        assert 'provider' in service.patterns
        assert 'date' in service.patterns
        assert 'invoice_number' in service.patterns
        
        # Verificar que cada categoría tiene patrones
        for category, patterns in service.patterns.items():
            assert isinstance(patterns, list)
            assert len(patterns) > 0
    
    def test_supported_formats_configuration(self):
        """Test: Verificar configuración de formatos soportados."""
        service = OCRService()
        
        expected_formats = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.pdf']
        assert service.supported_formats == expected_formats
