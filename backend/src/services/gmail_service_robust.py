"""
Servicio robusto para integración con Gmail API.
Maneja la conexión, autenticación y procesamiento de correos electrónicos con mejor manejo de errores.
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

class RobustGmailService:
    """Servicio robusto para manejo de Gmail API con mejor manejo de errores."""
    
    def __init__(self):
        self.service = None
        self.credentials = None
        self.is_configured = False
        
    def check_configuration(self) -> Dict[str, Any]:
        """
        Verificar la configuración de Gmail API.
        
        Returns:
            Dict con estado de configuración
        """
        config_status = {
            'credentials_file_exists': False,
            'token_file_exists': False,
            'is_configured': False,
            'error_message': None
        }
        
        try:
            # Verificar archivo de credenciales
            if os.path.exists('credentials.json'):
                config_status['credentials_file_exists'] = True
            else:
                config_status['error_message'] = "Archivo credentials.json no encontrado"
                return config_status
            
            # Verificar archivo de token
            if os.path.exists('token.json'):
                config_status['token_file_exists'] = True
            
            # Verificar que el archivo de credenciales sea válido
            try:
                with open('credentials.json', 'r') as f:
                    credentials_data = json.load(f)
                    if 'installed' not in credentials_data:
                        config_status['error_message'] = "Formato de credentials.json inválido"
                        return config_status
            except json.JSONDecodeError:
                config_status['error_message'] = "credentials.json no es un JSON válido"
                return config_status
            
            config_status['is_configured'] = True
            return config_status
            
        except Exception as e:
            config_status['error_message'] = f"Error verificando configuración: {str(e)}"
            return config_status
    
    def authenticate(self) -> Dict[str, Any]:
        """
        Autenticar con Gmail API con manejo robusto de errores.
        
        Returns:
            Dict con resultado de autenticación
        """
        result = {
            'success': False,
            'authenticated': False,
            'error_message': None,
            'requires_setup': False
        }
        
        try:
            # Verificar configuración
            config_status = self.check_configuration()
            if not config_status['is_configured']:
                result['error_message'] = config_status['error_message']
                result['requires_setup'] = True
                return result
            
            # Verificar si ya tenemos credenciales válidas
            if os.path.exists('token.json'):
                try:
                    self.credentials = Credentials.from_authorized_user_file('token.json', SCOPES)
                except Exception as e:
                    logger.warning(f"Error cargando token existente: {e}")
                    self.credentials = None
            
            # Si no hay credenciales válidas, solicitar autorización
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    try:
                        self.credentials.refresh(Request())
                        logger.info("Token renovado exitosamente")
                    except Exception as refresh_error:
                        logger.warning(f"Error al renovar token: {refresh_error}. Solicitando nueva autorización.")
                        self.credentials = None
                
                if not self.credentials:
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            'credentials.json', SCOPES
                        )
                        self.credentials = flow.run_local_server(port=0)
                        logger.info("Nueva autorización completada")
                    except Exception as flow_error:
                        result['error_message'] = f"Error en autorización: {str(flow_error)}"
                        return result
                
                # Guardar credenciales para uso futuro
                try:
                    with open('token.json', 'w') as token:
                        token.write(self.credentials.to_json())
                    logger.info("Token guardado exitosamente")
                except Exception as save_error:
                    logger.warning(f"Error al guardar token: {save_error}")
            
            # Construir servicio de Gmail
            self.service = build('gmail', 'v1', credentials=self.credentials)
            
            # Probar la conexión
            try:
                profile = self.service.users().getProfile(userId='me').execute()
                logger.info(f"Autenticación exitosa para: {profile.get('emailAddress')}")
            except Exception as test_error:
                result['error_message'] = f"Error probando conexión: {str(test_error)}"
                return result
            
            result['success'] = True
            result['authenticated'] = True
            return result
            
        except FileNotFoundError as e:
            result['error_message'] = f"Archivo no encontrado: {str(e)}"
            result['requires_setup'] = True
            return result
        except Exception as e:
            result['error_message'] = f"Error en autenticación: {str(e)}"
            return result
    
    def get_auth_status(self) -> Dict[str, Any]:
        """
        Obtener estado de autenticación.
        
        Returns:
            Dict con estado de autenticación
        """
        try:
            config_status = self.check_configuration()
            
            if not config_status['is_configured']:
                return {
                    'authenticated': False,
                    'message': 'Gmail no configurado. Se requiere credentials.json',
                    'requires_setup': True,
                    'config_status': config_status
                }
            
            # Intentar autenticar
            auth_result = self.authenticate()
            
            if auth_result['success']:
                return {
                    'authenticated': True,
                    'message': 'Autenticado correctamente con Gmail API',
                    'requires_setup': False,
                    'config_status': config_status
                }
            else:
                return {
                    'authenticated': False,
                    'message': auth_result['error_message'],
                    'requires_setup': auth_result['requires_setup'],
                    'config_status': config_status
                }
                
        except Exception as e:
            return {
                'authenticated': False,
                'message': f'Error verificando estado: {str(e)}',
                'requires_setup': True,
                'config_status': {'is_configured': False}
            }
    
    def search_emails_safe(self, query: str = "has:attachment", max_results: int = 10) -> Dict[str, Any]:
        """
        Buscar correos electrónicos con manejo seguro de errores.
        
        Args:
            query: Query de búsqueda de Gmail
            max_results: Número máximo de resultados
            
        Returns:
            Dict con resultado de búsqueda
        """
        result = {
            'success': False,
            'emails': [],
            'total': 0,
            'error_message': None
        }
        
        try:
            if not self.service:
                auth_result = self.authenticate()
                if not auth_result['success']:
                    result['error_message'] = auth_result['error_message']
                    return result
            
            # Buscar mensajes
            search_results = self.service.users().messages().list(
                userId='me', 
                q=query, 
                maxResults=max_results
            ).execute()
            
            messages = search_results.get('messages', [])
            emails = []
            
            for message in messages:
                try:
                    email_data = self.get_email_details_safe(message['id'])
                    if email_data:
                        emails.append(email_data)
                except Exception as email_error:
                    logger.warning(f"Error procesando email {message['id']}: {email_error}")
                    continue
            
            result['success'] = True
            result['emails'] = emails
            result['total'] = len(emails)
            return result
            
        except HttpError as e:
            result['error_message'] = f"Error de Gmail API: {str(e)}"
            return result
        except Exception as e:
            result['error_message'] = f"Error en búsqueda: {str(e)}"
            return result
    
    def get_email_details_safe(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener detalles de un email con manejo seguro de errores.
        
        Args:
            message_id: ID del mensaje
            
        Returns:
            Dict con detalles del email o None si hay error
        """
        try:
            if not self.service:
                return None
            
            message = self.service.users().messages().get(
                userId='me', 
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload'].get('headers', [])
            
            return {
                'id': message_id,
                'subject': self._get_header_value(headers, 'Subject'),
                'from': self._get_header_value(headers, 'From'),
                'date': self._get_header_value(headers, 'Date'),
                'body': self._extract_body_safe(message['payload']),
                'attachments': self._extract_attachments_safe(message['payload'])
            }
            
        except Exception as e:
            logger.warning(f"Error obteniendo detalles del email {message_id}: {e}")
            return None
    
    def _get_header_value(self, headers: List[Dict], name: str) -> str:
        """Obtener valor de header por nombre."""
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return ""
    
    def _extract_body_safe(self, payload: Dict) -> str:
        """Extraer cuerpo del email de forma segura."""
        try:
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data')
                        if data:
                            return base64.urlsafe_b64decode(data).decode('utf-8')
            elif payload['mimeType'] == 'text/plain':
                data = payload['body'].get('data')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
            return ""
        except Exception as e:
            logger.warning(f"Error extrayendo cuerpo del email: {e}")
            return ""
    
    def _extract_attachments_safe(self, payload: Dict) -> List[Dict]:
        """Extraer adjuntos de forma segura."""
        try:
            attachments = []
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['filename']:
                        attachments.append({
                            'filename': part['filename'],
                            'mime_type': part['mimeType'],
                            'size': part['body'].get('size', 0)
                        })
            return attachments
        except Exception as e:
            logger.warning(f"Error extrayendo adjuntos: {e}")
            return []
    
    def get_stats_safe(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de Gmail de forma segura.
        
        Returns:
            Dict con estadísticas
        """
        stats = {
            'success': False,
            'total_emails_7d': 0,
            'emails_with_attachments_7d': 0,
            'unread_emails_7d': 0,
            'attachment_rate': 0.0,
            'error_message': None
        }
        
        try:
            # Buscar emails de los últimos 7 días
            date_7d_ago = (datetime.now() - timedelta(days=7)).strftime('%Y/%m/%d')
            query_7d = f"after:{date_7d_ago}"
            
            # Total de emails
            total_result = self.search_emails_safe(query_7d, 100)
            if total_result['success']:
                stats['total_emails_7d'] = total_result['total']
            
            # Emails con adjuntos
            attachments_result = self.search_emails_safe(f"{query_7d} has:attachment", 100)
            if attachments_result['success']:
                stats['emails_with_attachments_7d'] = attachments_result['total']
            
            # Emails no leídos
            unread_result = self.search_emails_safe(f"{query_7d} is:unread", 100)
            if unread_result['success']:
                stats['unread_emails_7d'] = unread_result['total']
            
            # Calcular tasa de adjuntos
            if stats['total_emails_7d'] > 0:
                stats['attachment_rate'] = (stats['emails_with_attachments_7d'] / stats['total_emails_7d']) * 100
            
            stats['success'] = True
            return stats
            
        except Exception as e:
            stats['error_message'] = f"Error obteniendo estadísticas: {str(e)}"
            return stats
