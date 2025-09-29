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
                'attachments': self._extract_attachments(message['payload']),
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
    
    def _extract_attachments(self, payload: Dict) -> List[Dict[str, Any]]:
        """Extraer información de archivos adjuntos."""
        attachments = []
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['filename']:
                    attachment = {
                        'filename': part['filename'],
                        'mime_type': part['mimeType'],
                        'size': part['body'].get('size', 0),
                        'attachment_id': part['body'].get('attachmentId')
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
            'cobro', 'charge', 'servicio', 'service'
        ]
        
        # Verificar si hay palabras clave en el asunto o cuerpo
        has_keywords = any(keyword in subject or keyword in body for keyword in invoice_keywords)
        
        # Verificar si hay archivos adjuntos (PDF, imágenes)
        has_attachments = any(
            attachment['mime_type'] in ['application/pdf', 'image/jpeg', 'image/png']
            for attachment in attachments
        )
        
        return has_keywords and has_attachments
    
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
        
        # Intentar extraer del asunto
        if 'factura' in subject.lower():
            # Buscar patrones como "Factura de [PROVEEDOR]"
            parts = subject.split()
            for i, part in enumerate(parts):
                if part.lower() in ['de', 'from'] and i + 1 < len(parts):
                    return parts[i + 1].title()
        
        return "Proveedor Desconocido"
    
    def _extract_amount(self, email_data: Dict[str, Any]) -> float:
        """Extraer monto de la factura."""
        import re
        
        text = f"{email_data.get('subject', '')} {email_data.get('body', '')}"
        
        # Buscar patrones de monto
        patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # $1,234.56
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*pesos',  # 1,234.56 pesos
            r'monto[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # monto: $1,234.56
            r'total[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # total: $1,234.56
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
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
