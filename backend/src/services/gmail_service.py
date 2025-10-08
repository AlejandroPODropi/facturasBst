"""
Servicio para integración con Gmail API.
Maneja la conexión, autenticación y procesamiento de correos electrónicos.
"""

import os
import base64
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.database import get_db
from src.models import Invoice, User, InvoiceStatus, ExpenseCategory, PaymentMethod
from sqlalchemy.orm import Session

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Scopes necesarios para Gmail API
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

class GmailService:
    """Servicio para manejo de Gmail API."""
    
    def __init__(self):
        self.service = None
        self.credentials = None
        
    def authenticate(self) -> bool:
        """
        Autenticar con Gmail API.
        
        Returns:
            bool: True si la autenticación fue exitosa
        """
        try:
            # Verificar si ya tenemos credenciales válidas
            if os.path.exists('token.json'):
                self.credentials = Credentials.from_authorized_user_file('token.json', SCOPES)
            
            # Si no hay credenciales válidas, solicitar autorización
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES
                    )
                    self.credentials = flow.run_local_server(port=0)
                
                # Guardar credenciales para uso futuro
                with open('token.json', 'w') as token:
                    token.write(self.credentials.to_json())
            
            # Construir servicio de Gmail
            self.service = build('gmail', 'v1', credentials=self.credentials)
            logger.info("Autenticación con Gmail API exitosa")
            return True
            
        except Exception as e:
            logger.error(f"Error en autenticación con Gmail API: {str(e)}")
            return False
    
    def search_emails(self, query: str = "has:attachment", max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Buscar correos electrónicos con criterios específicos.
        
        Args:
            query: Query de búsqueda de Gmail
            max_results: Número máximo de resultados
            
        Returns:
            Lista de correos encontrados
        """
        try:
            if not self.service:
                if not self.authenticate():
                    logger.error("No se pudo autenticar con Gmail API")
                    return []
            
            # Buscar mensajes
            results = self.service.users().messages().list(
                userId='me', 
                q=query, 
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                email_data = self.get_email_details(message['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except HttpError as error:
            logger.error(f"Error al buscar correos: {error}")
            return []
    
    def get_email_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener detalles de un correo específico.
        
        Args:
            message_id: ID del mensaje
            
        Returns:
            Diccionario con detalles del correo
        """
        try:
            message = self.service.users().messages().get(
                userId='me', 
                id=message_id, 
                format='full'
            ).execute()
            
            headers = message['payload'].get('headers', [])
            
            # Extraer información del header
            email_data = {
                'id': message_id,
                'thread_id': message['threadId'],
                'subject': self._get_header_value(headers, 'Subject'),
                'from': self._get_header_value(headers, 'From'),
                'to': self._get_header_value(headers, 'To'),
                'date': self._get_header_value(headers, 'Date'),
                'body': self._extract_body(message['payload']),
                'attachments': self._extract_attachments(message['payload'], message_id),
                'labels': message.get('labelIds', [])
            }
            
            return email_data
            
        except HttpError as error:
            logger.error(f"Error al obtener detalles del correo {message_id}: {error}")
            return None
    
    def _get_header_value(self, headers: List[Dict], name: str) -> str:
        """Obtener valor de un header específico."""
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return ""
    
    def _extract_body(self, payload: Dict) -> str:
        """Extraer el cuerpo del correo."""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
        else:
            if payload['mimeType'] == 'text/plain':
                data = payload['body'].get('data')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body
    
    def _extract_attachments(self, payload: Dict, message_id: str = None) -> List[Dict[str, Any]]:
        """Extraer información de archivos adjuntos."""
        attachments = []
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['filename']:
                    attachment = {
                        'filename': part['filename'],
                        'mime_type': part['mimeType'],
                        'size': part['body'].get('size', 0),
                        'attachment_id': part['body'].get('attachmentId'),
                        'message_id': message_id
                    }
                    attachments.append(attachment)
        
        return attachments
    
    def download_attachment(self, message_id: str, attachment_id: str) -> Optional[bytes]:
        """
        Descargar un archivo adjunto.
        
        Args:
            message_id: ID del mensaje
            attachment_id: ID del adjunto
            
        Returns:
            Contenido del archivo como bytes
        """
        try:
            attachment = self.service.users().messages().attachments().get(
                userId='me',
                messageId=message_id,
                id=attachment_id
            ).execute()
            
            data = attachment['data']
            return base64.urlsafe_b64decode(data)
            
        except HttpError as error:
            logger.error(f"Error al descargar adjunto: {error}")
            return None
    
    def mark_as_read(self, message_id: str) -> bool:
        """
        Marcar un correo como leído.
        
        Args:
            message_id: ID del mensaje
            
        Returns:
            True si fue exitoso
        """
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
            
        except HttpError as error:
            logger.error(f"Error al marcar como leído: {error}")
            return False


class InvoiceEmailProcessor:
    """Procesador de correos para extraer facturas."""
    
    def __init__(self, gmail_service: GmailService):
        self.gmail_service = gmail_service
        
    def is_invoice_email(self, email_data: Dict[str, Any]) -> bool:
        """
        Determinar si un correo contiene una factura.
        
        Args:
            email_data: Datos del correo
            
        Returns:
            True si parece ser una factura
        """
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        attachments = email_data.get('attachments', [])
        
        # Palabras clave que indican facturas
        invoice_keywords = [
            'factura', 'invoice', 'recibo', 'comprobante',
            'gasto', 'expense', 'pago', 'payment',
            'cobro', 'charge', 'servicio', 'service',
            'bill', 'billing', 'cuenta', 'account'
        ]
        
        # Verificar si hay palabras clave en el asunto o cuerpo
        has_keywords = any(keyword in subject or keyword in body for keyword in invoice_keywords)
        
        # Verificar patrones específicos de facturación colombiana
        has_invoice_pattern = self._has_invoice_pattern(email_data.get('subject', ''))
        
        # Verificar si hay archivos adjuntos (PDF, imágenes, ZIP)
        has_attachments = any(
            attachment['mime_type'] in [
                'application/pdf', 
                'image/jpeg', 
                'image/png',
                'application/zip',  # Agregar soporte para archivos ZIP
                'application/octet-stream'  # Agregar soporte para archivos binarios
            ]
            for attachment in attachments
        )
        
        # Es factura si tiene palabras clave O patrón de factura, Y tiene adjuntos
        return (has_keywords or has_invoice_pattern) and has_attachments
    
    def _has_invoice_pattern(self, subject: str) -> bool:
        """
        Detectar patrones específicos de facturación colombiana.
        
        Args:
            subject: Asunto del correo
            
        Returns:
            True si coincide con patrones de factura
        """
        import re
        
        # Patrón 1: Código;Empresa;CódigoFactura;Secuencia;Empresa
        # Ejemplo: 901294241;PAGOS AUTOMATICOS DE COLOMBIA SAS;FVFE255128;01;PAGOS AUTOMATICOS DE COLOMBIA SAS
        pattern1 = r'^\d{9,12};[A-Z\s\.\-]+;[A-Z0-9]{6,12};\d{2};[A-Z\s\.\-]+'
        
        # Patrón 2: Código numérico seguido de empresa
        # Ejemplo: 900632938;ESTRELLA ANDINA S.A.S
        pattern2 = r'^\d{9,12};[A-Z\s\.\-]+'
        
        # Patrón 3: Código alfanumérico de factura
        # Ejemplo: FVFE255128, UNFE383160, EDA2068
        pattern3 = r'[A-Z]{2,6}\d{6,12}'
        
        # Patrón 4: Formato genérico de factura
        # Ejemplo: "Factura 12345 – Empresa", "Factura [Número] – Cliente"
        pattern4 = r'factura\s+\d+.*–.*|invoice\s+\d+.*–.*'
        
        patterns = [pattern1, pattern2, pattern3, pattern4]
        
        for pattern in patterns:
            if re.search(pattern, subject, re.IGNORECASE):
                return True
        
        return False
    
    def extract_invoice_data(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extraer datos de factura del correo.
        
        Args:
            email_data: Datos del correo
            
        Returns:
            Diccionario con datos extraídos de la factura
        """
        # Datos básicos del correo
        invoice_data = {
            'provider': self._extract_provider(email_data),
            'amount': self._extract_amount(email_data),
            'date': self._extract_date(email_data),
            'description': self._extract_description(email_data),
            'email_subject': email_data.get('subject', ''),
            'email_from': email_data.get('from', ''),
            'attachments': email_data.get('attachments', []),
            'gmail_attachments': self._format_gmail_attachments(email_data.get('attachments', [])),
            'raw_email_data': email_data
        }
        
        return invoice_data
    
    def _extract_provider(self, email_data: Dict[str, Any]) -> str:
        """Extraer nombre del proveedor del correo."""
        from_email = email_data.get('from', '')
        subject = email_data.get('subject', '')
        
        # Intentar extraer del email
        if '@' in from_email:
            domain = from_email.split('@')[1]
            provider = domain.split('.')[0]
            return provider.title()
        
        # Intentar extraer del asunto usando patrones específicos
        provider = self._extract_provider_from_subject(subject)
        if provider != "Proveedor Desconocido":
            return provider
        
        # Intentar extraer del asunto (método genérico)
        if 'factura' in subject.lower():
            # Buscar patrones como "Factura de [PROVEEDOR]"
            parts = subject.split()
            for i, part in enumerate(parts):
                if part.lower() in ['de', 'from'] and i + 1 < len(parts):
                    return parts[i + 1].title()
        
        return "Proveedor Desconocido"
    
    def _extract_provider_from_subject(self, subject: str) -> str:
        """
        Extraer proveedor del asunto usando patrones específicos de facturación.
        
        Args:
            subject: Asunto del correo
            
        Returns:
            Nombre del proveedor o "Proveedor Desconocido"
        """
        import re
        
        # Patrón 1: Código;Empresa;CódigoFactura;Secuencia;Empresa
        # Ejemplo: 901294241;PAGOS AUTOMATICOS DE COLOMBIA SAS;FVFE255128;01;PAGOS AUTOMATICOS DE COLOMBIA SAS
        pattern1 = r'^\d{9,12};([A-Z\s\.\-]+);[A-Z0-9]{6,12};\d{2};[A-Z\s\.\-]+'
        match1 = re.search(pattern1, subject)
        if match1:
            provider = match1.group(1).strip()
            return self._clean_provider_name(provider)
        
        # Patrón 2: Código numérico seguido de empresa
        # Ejemplo: 900632938;ESTRELLA ANDINA S.A.S
        pattern2 = r'^\d{9,12};\s*([A-Z\s\.\-]+)'
        match2 = re.search(pattern2, subject)
        if match2:
            provider = match2.group(1).strip()
            return self._clean_provider_name(provider)
        
        # Patrón 3: Formato genérico con guión
        # Ejemplo: "Factura 12345 – Empresa", "Invoice 12345 – Cliente"
        pattern3 = r'factura\s+\d+.*–\s*([^–]+)|invoice\s+\d+.*–\s*([^–]+)'
        match3 = re.search(pattern3, subject, re.IGNORECASE)
        if match3:
            provider = (match3.group(1) or match3.group(2)).strip()
            return self._clean_provider_name(provider)
        
        return "Proveedor Desconocido"
    
    def _clean_provider_name(self, provider: str) -> str:
        """
        Limpiar y formatear el nombre del proveedor.
        
        Args:
            provider: Nombre del proveedor en bruto
            
        Returns:
            Nombre del proveedor limpio y formateado
        """
        # Remover caracteres especiales al final
        provider = provider.rstrip(';.,- ')
        
        # Convertir a formato título (primera letra de cada palabra en mayúscula)
        provider = provider.title()
        
        # Manejar casos especiales de empresas colombianas
        provider = provider.replace('S.A.S', 'S.A.S.')
        provider = provider.replace('S.A', 'S.A.')
        provider = provider.replace('Ltda', 'Ltda.')
        
        # Corregir casos donde se duplican los puntos
        provider = provider.replace('S.A..S.', 'S.A.S.')
        provider = provider.replace('S.A..', 'S.A.')
        
        # Asegurar que las siglas tengan puntos
        if provider.endswith('SAS') and not provider.endswith('S.A.S.'):
            provider = provider.replace('Sas', 'S.A.S.')
        elif provider.endswith('SA') and not provider.endswith('S.A.'):
            provider = provider.replace('Sa', 'S.A.')
        elif provider.endswith('LTDA') and not provider.endswith('Ltda.'):
            provider = provider.replace('Ltda', 'Ltda.')
        
        # Casos especiales para "S A S" (con espacios)
        if provider.endswith('S A S') and not provider.endswith('S.A.S.'):
            provider = provider.replace('S A S', 'S.A.S.')
        elif provider.endswith('S A') and not provider.endswith('S.A.'):
            provider = provider.replace('S A', 'S.A.')
        
        return provider
    
    def _extract_amount(self, email_data: Dict[str, Any]) -> float:
        """Extraer monto de la factura."""
        import re
        
        text = f"{email_data.get('subject', '')} {email_data.get('body', '')}"
        
        # Buscar patrones de monto más específicos para facturas colombianas
        patterns = [
            # Patrones colombianos: 1.000.000,50 o 1,000,000.50
            r'\$(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)',  # $1.000.000,50 o $1,000,000.50
            r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*pesos',  # 1.000.000,50 pesos
            r'monto[:\s]*\$?(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)',  # monto: $1.000.000,50
            r'total[:\s]*\$?(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)',  # total: $1.000.000,50
            r'valor[:\s]*\$?(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)',  # valor: $1.000.000,50
            r'suma[:\s]*\$?(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)',  # suma: $1.000.000,50
            # Patrones para números sin separadores
            r'\$(\d+(?:[.,]\d{2})?)',  # $1000000,50
            r'(\d+(?:[.,]\d{2})?)\s*pesos',  # 1000000,50 pesos
            # Patrones específicos de facturas electrónicas colombianas
            r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*COP',  # 1.000.000,50 COP
            r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*colombianos',  # 1.000.000,50 colombianos
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1)
                try:
                    # Manejar formato colombiano: 1.000.000,50 -> 1000000.50
                    if ',' in amount_str and '.' in amount_str:
                        # Formato: 1.000.000,50
                        amount_str = amount_str.replace('.', '').replace(',', '.')
                    elif ',' in amount_str and '.' not in amount_str:
                        # Verificar si es separador de miles o decimales
                        parts = amount_str.split(',')
                        if len(parts) == 2 and len(parts[1]) <= 2:
                            # Es decimal: 1000000,50
                            amount_str = amount_str.replace(',', '.')
                        else:
                            # Es separador de miles: 1,000,000
                            amount_str = amount_str.replace(',', '')
                    elif '.' in amount_str and ',' not in amount_str:
                        # Verificar si es separador de miles o decimales
                        parts = amount_str.split('.')
                        if len(parts) == 2 and len(parts[1]) <= 2:
                            # Es decimal: 1000000.50
                            pass  # Ya está en formato correcto
                        else:
                            # Es separador de miles: 1.000.000
                            amount_str = amount_str.replace('.', '')
                    
                    amount = float(amount_str)
                    if amount > 0:
                        return amount
                except ValueError:
                    continue
        
        return 0.0
    
    def _extract_date(self, email_data: Dict[str, Any]) -> datetime:
        """Extraer fecha de la factura."""
        from email.utils import parsedate_to_datetime
        
        date_str = email_data.get('date', '')
        if date_str:
            try:
                return parsedate_to_datetime(date_str)
            except:
                pass
        
        return datetime.now()
    
    def _extract_description(self, email_data: Dict[str, Any]) -> str:
        """Extraer descripción de la factura."""
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')
        
        # Usar el asunto como descripción principal
        if subject:
            return subject[:200]  # Limitar longitud
        
        # Si no hay asunto, usar parte del cuerpo
        if body:
            return body[:200]
        
        return "Factura recibida por email"
    
    def _format_gmail_attachments(self, attachments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Formatear información de archivos adjuntos para almacenamiento."""
        formatted_attachments = []
        
        for attachment in attachments:
            formatted_attachment = {
                'filename': attachment.get('filename', ''),
                'mime_type': attachment.get('mime_type', ''),
                'size': attachment.get('size', 0),
                'attachment_id': attachment.get('attachment_id', ''),
                'download_url': f"/api/v1/gmail/attachments/{attachment.get('message_id', '')}/{attachment.get('attachment_id', '')}"
            }
            formatted_attachments.append(formatted_attachment)
        
        return formatted_attachments


def process_gmail_invoices(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Procesar correos de Gmail para extraer facturas.
    
    Args:
        db: Sesión de base de datos
        limit: Número máximo de correos a procesar
        
    Returns:
        Lista de facturas procesadas
    """
    gmail_service = GmailService()
    processor = InvoiceEmailProcessor(gmail_service)
    
    # Autenticar con Gmail
    if not gmail_service.authenticate():
        logger.error("No se pudo autenticar con Gmail API")
        return []
    
    # Buscar correos recientes con adjuntos
    emails = gmail_service.search_emails(
        query="has:attachment newer_than:7d",
        max_results=limit
    )
    
    processed_invoices = []
    
    for email_data in emails:
        try:
            # Verificar si es una factura
            if not processor.is_invoice_email(email_data):
                continue
            
            # Extraer datos de la factura
            invoice_data = processor.extract_invoice_data(email_data)
            
            # Crear factura en la base de datos
            invoice = create_invoice_from_email(db, invoice_data)
            
            if invoice:
                processed_invoices.append({
                    'invoice_id': invoice.id,
                    'provider': invoice.provider,
                    'amount': invoice.amount,
                    'email_subject': invoice_data['email_subject']
                })
                
                # Marcar correo como leído
                gmail_service.mark_as_read(email_data['id'])
                
        except Exception as e:
            logger.error(f"Error procesando correo {email_data.get('id', 'unknown')}: {str(e)}")
            continue
    
    return processed_invoices


def create_invoice_from_email(db: Session, invoice_data: Dict[str, Any]) -> Optional[Invoice]:
    """
    Crear factura en la base de datos a partir de datos de email.
    
    Args:
        db: Sesión de base de datos
        invoice_data: Datos extraídos del email
        
    Returns:
        Factura creada o None si hubo error
    """
    try:
        # Obtener usuario por defecto (en un sistema real, esto sería más sofisticado)
        default_user = db.query(User).first()
        if not default_user:
            logger.error("No hay usuarios en el sistema")
            return None
        
        # Crear factura
        invoice = Invoice(
            user_id=default_user.id,
            provider=invoice_data['provider'],
            amount=invoice_data['amount'],
            date=invoice_data['date'],
            description=invoice_data['description'],
            category=ExpenseCategory.OTROS,  # Categoría por defecto
            payment_method=PaymentMethod.OTROS,  # Método por defecto
            status=InvoiceStatus.PENDING,
            file_path=None,  # Se procesará después
            validation_notes=f"Factura extraída automáticamente de email: {invoice_data['email_subject']}"
        )
        
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        logger.info(f"Factura creada: {invoice.id} - {invoice.provider} - ${invoice.amount}")
        return invoice
        
    except Exception as e:
        logger.error(f"Error creando factura: {str(e)}")
        db.rollback()
        return None
