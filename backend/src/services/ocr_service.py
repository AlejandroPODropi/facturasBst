"""
Servicio OCR para procesamiento de facturas físicas.
Utiliza Tesseract OCR para extraer texto de imágenes y PDFs de facturas.
"""

import os
import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from PIL import Image
import pytesseract
import fitz  # PyMuPDF para PDFs
import io
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OCRService:
    """Servicio para procesamiento OCR de facturas físicas."""
    
    def __init__(self):
        """Inicializar el servicio OCR."""
        # Configurar Tesseract (ajustar según el sistema)
        self.tesseract_config = '--oem 3 --psm 6'
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.pdf']
        
        # Diccionario de categorías por keywords (mejorado)
        self.categories = {
            "alimentacion": ["RESTAURANTE", "ALMUERZO", "COMIDA", "CAFETERIA", "BAR", "PIZZA", "HAMBURGUESA"],
            "combustible": ["GASOLINA", "ACPM", "EDS", "GL", "PETROBRAS", "TERPEL", "ESSO", "SHELL"],
            "transporte": ["TAXI", "UBER", "BUS", "PEAJE", "TRANSMILENIO", "SITP", "METRO"],
            "hospedaje": ["HOTEL", "HOSTAL", "ALOJAMIENTO", "HOSPEDAJE", "MOTEL"],
            "papeleria": ["PAPELERÍA", "ÚTILES", "OFICINA", "PAPEL", "LAPIZ", "BOLIGRAFO"],
            "farmacia": ["FARMACIA", "MEDICINA", "MEDICAMENTO", "DROGUERIA"],
            "supermercado": ["SUPERMERCADO", "MARKET", "TIENDA", "ALMACEN", "EXITO", "CARULLA"],
            "otros": ["VARIOS", "SUMINISTROS", "SERVICIOS"]
        }
        
        # Patrones mejorados para extraer información de facturas
        self.patterns = {
            'amount': [
                r'(TOTAL|A PAGAR|VALOR BRUTO|VALOR TOTAL)[:\s]*\$?\s*([0-9\.\,]+)',
                r'total[:\s]*\$?[\s]*([0-9,]+\.?[0-9]*)',
                r'monto[:\s]*\$?[\s]*([0-9,]+\.?[0-9]*)',
                r'importe[:\s]*\$?[\s]*([0-9,]+\.?[0-9]*)',
                r'valor[:\s]*\$?[\s]*([0-9,]+\.?[0-9]*)',
                r'\$[\s]*([0-9,]+\.?[0-9]*)',
                r'([0-9,]+\.?[0-9]*)[\s]*pesos?',
            ],
            'provider': [
                r'([A-Z\s\.]+S\.A\.S\.|[A-Z\s]+LTDA|[A-Z\s]+S\.A\.)',
                r'proveedor[:\s]*([^\n\r]+?)(?:\s+fecha|\s+total|\s+factura|$)',
                r'vendedor[:\s]*([^\n\r]+?)(?:\s+fecha|\s+total|\s+factura|$)',
                r'empresa[:\s]*([^\n\r]+?)(?:\s+fecha|\s+total|\s+factura|$)',
                r'razón social[:\s]*([^\n\r]+?)(?:\s+fecha|\s+total|\s+factura|$)',
            ],
            'date': [
                r'fecha[:\s]*([0-9]{4}[/\-\.][0-9]{1,2}[/\-\.][0-9]{1,2})',
                r'emisión[:\s]*([0-9]{4}[/\-\.][0-9]{1,2}[/\-\.][0-9]{1,2})',
                r'fecha[:\s]*([0-9]{1,2}[/\-\.][0-9]{1,2}[/\-\.][0-9]{2,4})',
                r'emisión[:\s]*([0-9]{1,2}[/\-\.][0-9]{1,2}[/\-\.][0-9]{2,4})',
                r'([0-9]{4}[/\-\.][0-9]{1,2}[/\-\.][0-9]{1,2})',
                r'([0-9]{1,2}[/\-\.][0-9]{1,2}[/\-\.][0-9]{2,4})',
            ],
            'invoice_number': [
                r'factura[:\s]*n[o°]?[:\s]*([0-9a-zA-Z\-]+)',
                r'no[:\s]*factura[:\s]*([0-9a-zA-Z\-]+)',
                r'comprobante[:\s]*n[o°]?[:\s]*([0-9a-zA-Z\-]+)',
            ],
            'nit': [
                r'NIT[:\s]*([0-9\-\.]+)',
                r'IDENTIFICACIÓN[:\s]*([0-9\-\.]+)',
            ],
            'payment_method': [
                r'(EFECTIVO|TARJETA|CONTADO|CREDITO|DEBITO|TRANSFERENCIA)',
                r'método de pago[:\s]*([^\n\r]+)',
            ]
        }
    
    def classify_expense(self, text: str) -> str:
        """
        Clasifica el gasto según keywords predefinidos.
        
        Args:
            text: Texto extraído de la factura
            
        Returns:
            str: Categoría del gasto
        """
        text_upper = text.upper()
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in text_upper:
                    return category.upper()
        return "OTROS"
    
    def is_supported_format(self, filename: str) -> bool:
        """
        Verificar si el formato del archivo es soportado.
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            bool: True si el formato es soportado
        """
        extension = Path(filename).suffix.lower()
        return extension in self.supported_formats
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extraer texto de una imagen usando Tesseract OCR.
        
        Args:
            image_path: Ruta de la imagen
            
        Returns:
            str: Texto extraído de la imagen
        """
        try:
            # Abrir imagen
            image = Image.open(image_path)
            
            # Convertir a RGB si es necesario
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extraer texto con Tesseract (mejorado)
            text = pytesseract.image_to_string(
                image, 
                config=self.tesseract_config,
                lang='spa+eng'  # Español e inglés
            ).upper()  # Convertir a mayúsculas para mejor matching
            
            logger.info(f"Texto extraído de imagen: {len(text)} caracteres")
            return text
            
        except Exception as e:
            logger.error(f"Error extrayendo texto de imagen {image_path}: {str(e)}")
            raise
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extraer texto de un PDF.
        
        Args:
            pdf_path: Ruta del PDF
            
        Returns:
            str: Texto extraído del PDF
        """
        try:
            text = ""
            doc = fitz.open(pdf_path)
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                
                # Intentar extraer texto directamente
                page_text = page.get_text()
                if page_text.strip():
                    text += page_text + "\n"
                else:
                    # Si no hay texto, convertir a imagen y usar OCR
                    pix = page.get_pixmap()
                    img_data = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_data))
                    
                    # Extraer texto con OCR
                    ocr_text = pytesseract.image_to_string(
                        img, 
                        config=self.tesseract_config,
                        lang='spa+eng'
                    )
                    text += ocr_text + "\n"
            
            doc.close()
            logger.info(f"Texto extraído de PDF: {len(text)} caracteres")
            return text
            
        except Exception as e:
            logger.error(f"Error extrayendo texto de PDF {pdf_path}: {str(e)}")
            raise
    
    def extract_text_from_file(self, file_path: str) -> str:
        """
        Extraer texto de un archivo (imagen o PDF).
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            str: Texto extraído del archivo
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        extension = Path(file_path).suffix.lower()
        
        if extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif extension in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
            return self.extract_text_from_image(file_path)
        else:
            raise ValueError(f"Formato de archivo no soportado: {extension}")
    
    def extract_invoice_data(self, text: str) -> Dict[str, Any]:
        """
        Extraer datos estructurados de una factura del texto OCR.
        
        Args:
            text: Texto extraído por OCR
            
        Returns:
            Dict con los datos extraídos de la factura
        """
        extracted_data = {
            'amount': None,
            'provider': None,
            'date': None,
            'invoice_number': None,
            'nit': None,
            'payment_method': None,
            'category': None,
            'raw_text': text,
            'confidence': 0.0
        }
        
        # Limpiar texto
        clean_text = re.sub(r'\s+', ' ', text.lower())
        
        # Extraer monto
        amount = self._extract_amount(clean_text)
        if amount:
            extracted_data['amount'] = amount
        
        # Extraer proveedor
        provider = self._extract_provider(clean_text)
        if provider:
            extracted_data['provider'] = provider
        
        # Extraer fecha
        date = self._extract_date(clean_text)
        if date:
            extracted_data['date'] = date
        
        # Extraer número de factura
        invoice_number = self._extract_invoice_number(clean_text)
        if invoice_number:
            extracted_data['invoice_number'] = invoice_number
        
        # Extraer NIT
        nit = self._extract_nit(clean_text)
        if nit:
            extracted_data['nit'] = nit
        
        # Extraer método de pago
        payment_method = self._extract_payment_method(clean_text)
        if payment_method:
            extracted_data['payment_method'] = payment_method
        
        # Clasificar categoría automáticamente
        category = self.classify_expense(text)
        extracted_data['category'] = category
        
        # Calcular confianza basada en datos extraídos
        confidence = self._calculate_confidence(extracted_data)
        extracted_data['confidence'] = confidence
        
        return extracted_data
    
    def _extract_amount(self, text: str) -> Optional[float]:
        """Extraer monto de la factura."""
        for pattern in self.patterns['amount']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    # Manejar patrones con grupos múltiples
                    if isinstance(matches[0], tuple):
                        amount_str = matches[0][1] if len(matches[0]) > 1 else matches[0][0]
                    else:
                        amount_str = matches[0]
                    
                    amount_str = amount_str.strip()
                    # Remover comas y puntos (formato colombiano: 1.000.000,50)
                    amount_str = amount_str.replace('.', '').replace(',', '.')
                    amount = float(amount_str)
                    if amount > 0:
                        return amount
                except ValueError:
                    continue
        return None
    
    def _extract_provider(self, text: str) -> Optional[str]:
        """Extraer nombre del proveedor."""
        for pattern in self.patterns['provider']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                provider = matches[0].strip()
                # Filtrar resultados muy cortos o que contengan palabras clave
                if len(provider) > 2 and not any(keyword in provider.lower() for keyword in ['fecha', 'total', 'factura', 'visible']):
                    return provider.title()
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extraer fecha de la factura."""
        for pattern in self.patterns['date']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                date_str = matches[0].strip()
                try:
                    # Intentar parsear la fecha
                    parsed_date = self._parse_date(date_str)
                    if parsed_date:
                        return parsed_date.isoformat()
                except ValueError:
                    continue
        return None
    
    def _extract_invoice_number(self, text: str) -> Optional[str]:
        """Extraer número de factura."""
        for pattern in self.patterns['invoice_number']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                invoice_num = matches[0].strip()
                if len(invoice_num) > 0:
                    return invoice_num
        return None
    
    def _extract_nit(self, text: str) -> Optional[str]:
        """Extraer NIT de la factura."""
        for pattern in self.patterns['nit']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                nit = matches[0].strip()
                if len(nit) > 0:
                    return nit
        return None
    
    def _extract_payment_method(self, text: str) -> Optional[str]:
        """Extraer método de pago de la factura."""
        for pattern in self.patterns['payment_method']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                method = matches[0].strip()
                if len(method) > 0:
                    return method
        return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parsear fecha en diferentes formatos."""
        formats = [
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%d.%m.%Y',
            '%d/%m/%y',
            '%d-%m-%y',
            '%d.%m.%y',
            '%Y-%m-%d',
            '%Y/%m/%d',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def _calculate_confidence(self, extracted_data: Dict[str, Any]) -> float:
        """Calcular nivel de confianza de la extracción."""
        confidence = 0.0
        
        if extracted_data['amount']:
            confidence += 0.3  # El monto es importante
        if extracted_data['provider']:
            confidence += 0.25
        if extracted_data['date']:
            confidence += 0.15
        if extracted_data['invoice_number']:
            confidence += 0.1
        if extracted_data['nit']:
            confidence += 0.1
        if extracted_data['payment_method']:
            confidence += 0.05
        if extracted_data['category'] and extracted_data['category'] != 'OTROS':
            confidence += 0.05
        
        return round(min(confidence, 1.0), 2)
    
    def process_invoice_file(self, file_path: str) -> Dict[str, Any]:
        """
        Procesar un archivo de factura completo.
        
        Args:
            file_path: Ruta del archivo de factura
            
        Returns:
            Dict con los datos extraídos y metadatos
        """
        try:
            # Verificar formato soportado
            if not self.is_supported_format(file_path):
                raise ValueError(f"Formato de archivo no soportado: {Path(file_path).suffix}")
            
            # Extraer texto
            text = self.extract_text_from_file(file_path)
            
            if not text.strip():
                raise ValueError("No se pudo extraer texto del archivo")
            
            # Extraer datos estructurados
            invoice_data = self.extract_invoice_data(text)
            
            # Agregar metadatos
            invoice_data.update({
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'processed_at': datetime.now().isoformat(),
                'text_length': len(text)
            })
            
            logger.info(f"Factura procesada: {invoice_data['confidence']:.2f} confianza")
            return invoice_data
            
        except Exception as e:
            logger.error(f"Error procesando factura {file_path}: {str(e)}")
            raise


# Instancia global del servicio
ocr_service = OCRService()
