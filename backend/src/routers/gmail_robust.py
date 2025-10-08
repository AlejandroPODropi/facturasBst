"""
Router robusto para endpoints de integración con Gmail API.
Maneja la sincronización y procesamiento de correos electrónicos con mejor manejo de errores.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import os

from src.database import get_db
from src.services.gmail_service_robust import RobustGmailService
from src.services.gmail_service import process_gmail_invoices
from src.schemas import MessageResponse

router = APIRouter(tags=["gmail"])

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/auth/status")
async def get_auth_status():
    """
    Verificar estado de autenticación con Gmail API.
    
    Returns:
        Dict con estado de autenticación y configuración
    """
    try:
        gmail_service = RobustGmailService()
        status_result = gmail_service.get_auth_status()
        
        return {
            "authenticated": status_result['authenticated'],
            "message": status_result['message'],
            "requires_setup": status_result['requires_setup'],
            "config_status": status_result.get('config_status', {})
        }
        
    except Exception as e:
        logger.error(f"Error verificando estado de autenticación: {str(e)}")
        return {
            "authenticated": False,
            "message": f"Error verificando estado: {str(e)}",
            "requires_setup": True,
            "config_status": {"is_configured": False}
        }


@router.post("/auth/authenticate")
async def authenticate_gmail():
    """
    Iniciar proceso de autenticación con Gmail API.
    
    Returns:
        Dict con resultado de autenticación
    """
    try:
        gmail_service = RobustGmailService()
        auth_result = gmail_service.authenticate()
        
        if auth_result['success']:
            return {
                "success": True,
                "message": "Autenticación exitosa con Gmail API",
                "authenticated": True
            }
        else:
            return {
                "success": False,
                "message": auth_result['error_message'],
                "authenticated": False,
                "requires_setup": auth_result['requires_setup']
            }
            
    except Exception as e:
        logger.error(f"Error en autenticación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en autenticación: {str(e)}"
        )


@router.get("/auth/url")
async def get_auth_url():
    """
    Obtener URL de autorización para Gmail API.
    
    Returns:
        Dict con URL de autorización
    """
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        
        # Verificar que existe credentials.json
        if not os.path.exists('credentials.json'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Archivo credentials.json no encontrado"
            )
        
        # Crear flujo de autorización
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', 
            ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']
        )
        
        # Generar URL de autorización
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'  # Para aplicaciones instaladas
        )
        
        return {
            "success": True,
            "auth_url": auth_url,
            "message": "Visita la URL para autorizar la aplicación"
        }
        
    except Exception as e:
        logger.error(f"Error generando URL de autorización: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando URL de autorización: {str(e)}"
        )


@router.post("/auth/callback")
async def handle_auth_callback(code: str = Query(..., description="Código de autorización")):
    """
    Manejar callback de autorización de Gmail API.
    
    Args:
        code: Código de autorización recibido de Google
        
    Returns:
        Dict con resultado de autorización
    """
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        
        # Verificar que existe credentials.json
        if not os.path.exists('credentials.json'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Archivo credentials.json no encontrado"
            )
        
        # Crear flujo de autorización
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', 
            ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']
        )
        
        # Configurar redirect_uri para aplicaciones instaladas
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        
        # Intercambiar código por token
        try:
            flow.fetch_token(code=code)
        except Exception as token_error:
            error_msg = str(token_error)
            logger.error(f"Error intercambiando código por token: {error_msg}")
            
            # Manejar errores específicos
            if "invalid_grant" in error_msg:
                if "Malformed auth code" in error_msg:
                    detail = "El código de autorización está mal formateado. Por favor, obtén un nuevo código."
                elif "expired" in error_msg.lower():
                    detail = "El código de autorización ha expirado. Por favor, obtén un nuevo código."
                else:
                    detail = "Código de autorización inválido. Por favor, obtén un nuevo código."
            elif "redirect_uri" in error_msg:
                detail = "Error de configuración OAuth. El redirect_uri no está configurado correctamente."
            else:
                detail = f"Error en autorización: {error_msg}"
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=detail
            )
        
        # Guardar credenciales
        credentials = flow.credentials
        try:
            with open('token.json', 'w') as token_file:
                token_file.write(credentials.to_json())
        except Exception as save_error:
            logger.error(f"Error guardando token: {str(save_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error guardando token: {str(save_error)}"
            )
        
        return {
            "success": True,
            "message": "Autorización exitosa. Token guardado.",
            "authenticated": True
        }
        
    except Exception as e:
        logger.error(f"Error en callback de autorización: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en callback de autorización: {str(e)}"
        )


@router.get("/auth/simple")
async def get_simple_auth_url():
    """
    Obtener URL de autorización simple para Gmail API (sin redirect_uri).
    
    Returns:
        Dict con URL de autorización y instrucciones
    """
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        
        # Verificar que existe credentials.json
        if not os.path.exists('credentials.json'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Archivo credentials.json no encontrado"
            )
        
        # Crear flujo de autorización
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', 
            ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']
        )
        
        # Generar URL de autorización con redirect_uri específico
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'  # Para aplicaciones instaladas
        )
        
        return {
            "success": True,
            "auth_url": auth_url,
            "message": "Visita la URL para autorizar la aplicación. Copia el código de autorización y úsalo en /auth/callback",
            "instructions": [
                "1. Visita la URL de autorización",
                "2. Autoriza la aplicación en Google",
                "3. Copia el código de autorización que aparece",
                "4. Usa el endpoint /auth/callback con el código"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error generando URL de autorización simple: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando URL de autorización simple: {str(e)}"
        )


@router.get("/auth/manual")
async def get_manual_auth_instructions():
    """
    Obtener instrucciones para autorización manual de Gmail API.
    
    Returns:
        Dict con instrucciones detalladas para autorización manual
    """
    try:
        # Verificar que existe credentials.json
        if not os.path.exists('credentials.json'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Archivo credentials.json no encontrado"
            )
        
        # Leer el archivo de credenciales para obtener el client_id
        import json
        with open('credentials.json', 'r') as f:
            credentials_data = json.load(f)
        
        client_id = credentials_data.get('installed', {}).get('client_id', 'CLIENT_ID_NOT_FOUND')
        
        # Construir URL de autorización manual
        scopes = 'https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.modify'
        auth_url = f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={client_id}&scope={scopes}&access_type=offline&redirect_uri=urn:ietf:wg:oauth:2.0:oob"
        
        return {
            "success": True,
            "auth_url": auth_url,
            "client_id": client_id,
            "message": "Autorización manual de Gmail API",
            "instructions": [
                "1. Visita la URL de autorización proporcionada",
                "2. Inicia sesión con tu cuenta de Google",
                "3. Autoriza la aplicación 'Facturas BST'",
                "4. Copia el código de autorización que aparece en la pantalla",
                "5. Usa el endpoint POST /auth/callback con el código",
                "6. El token se guardará automáticamente"
            ],
            "note": "Si ves un error de redirect_uri, necesitas configurar 'urn:ietf:wg:oauth:2.0:oob' en Google Cloud Console"
        }
        
    except Exception as e:
        logger.error(f"Error generando instrucciones de autorización manual: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando instrucciones de autorización manual: {str(e)}"
        )


@router.get("/emails/search")
async def search_emails(
    query: str = Query(default="has:attachment", description="Query de búsqueda de Gmail"),
    max_results: int = Query(default=10, ge=1, le=100, description="Número máximo de resultados")
):
    """
    Buscar correos electrónicos con criterios específicos.
    
    Args:
        query: Query de búsqueda de Gmail
        max_results: Número máximo de resultados (1-100)
        
    Returns:
        Dict con correos encontrados
    """
    try:
        gmail_service = RobustGmailService()
        search_result = gmail_service.search_emails_safe(query, max_results)
        
        if search_result['success']:
            return {
                "success": True,
                "emails": search_result['emails'],
                "total": search_result['total'],
                "query": query,
                "max_results": max_results
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=search_result['error_message']
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error buscando emails: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error buscando emails: {str(e)}"
        )


@router.get("/stats")
async def get_gmail_stats():
    """
    Obtener estadísticas de Gmail.
    
    Returns:
        Dict con estadísticas de correos
    """
    try:
        gmail_service = RobustGmailService()
        stats_result = gmail_service.get_stats_safe()
        
        if stats_result['success']:
            return {
                "success": True,
                "total_emails_7d": stats_result['total_emails_7d'],
                "emails_with_attachments_7d": stats_result['emails_with_attachments_7d'],
                "unread_emails_7d": stats_result['unread_emails_7d'],
                "attachment_rate": round(stats_result['attachment_rate'], 2)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=stats_result['error_message']
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )


@router.get("/config/check")
async def check_gmail_config():
    """
    Verificar configuración de Gmail API.
    
    Returns:
        Dict con estado de configuración
    """
    try:
        gmail_service = RobustGmailService()
        config_status = gmail_service.check_configuration()
        
        return {
            "is_configured": config_status['is_configured'],
            "credentials_file_exists": config_status['credentials_file_exists'],
            "token_file_exists": config_status['token_file_exists'],
            "error_message": config_status.get('error_message'),
            "setup_required": not config_status['is_configured']
        }
        
    except Exception as e:
        logger.error(f"Error verificando configuración: {str(e)}")
        return {
            "is_configured": False,
            "credentials_file_exists": False,
            "token_file_exists": False,
            "error_message": f"Error verificando configuración: {str(e)}",
            "setup_required": True
        }


@router.post("/test/connection")
async def test_gmail_connection():
    """
    Probar conexión con Gmail API.
    
    Returns:
        Dict con resultado de prueba de conexión
    """
    try:
        gmail_service = RobustGmailService()
        auth_result = gmail_service.authenticate()
        
        if auth_result['success']:
            # Probar búsqueda básica
            search_result = gmail_service.search_emails_safe("in:inbox", 1)
            
            if search_result['success']:
                return {
                    "success": True,
                    "message": "Conexión con Gmail API exitosa",
                    "authenticated": True,
                    "search_working": True
                }
            else:
                return {
                    "success": False,
                    "message": f"Autenticación exitosa pero error en búsqueda: {search_result['error_message']}",
                    "authenticated": True,
                    "search_working": False
                }
        else:
            return {
                "success": False,
                "message": auth_result['error_message'],
                "authenticated": False,
                "search_working": False,
                "requires_setup": auth_result['requires_setup']
            }
            
    except Exception as e:
        logger.error(f"Error probando conexión: {str(e)}")
        return {
            "success": False,
            "message": f"Error probando conexión: {str(e)}",
            "authenticated": False,
            "search_working": False,
            "requires_setup": True
        }


@router.get("/help/setup")
async def get_setup_help():
    """
    Obtener ayuda para configuración de Gmail API.
    
    Returns:
        Dict con instrucciones de configuración
    """
    return {
        "setup_instructions": {
            "step_1": "Crear proyecto en Google Cloud Console",
            "step_2": "Habilitar Gmail API",
            "step_3": "Crear credenciales OAuth 2.0",
            "step_4": "Descargar credentials.json",
            "step_5": "Colocar credentials.json en la raíz del backend",
            "step_6": "Autenticar desde el frontend"
        },
        "required_files": [
            "credentials.json (descargado de Google Cloud Console)",
            "token.json (generado automáticamente después de autenticar)"
        ],
        "scopes_required": [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.modify"
        ],
        "troubleshooting": {
            "credentials_not_found": "Verifica que credentials.json esté en la raíz del backend",
            "invalid_credentials": "Verifica que el archivo credentials.json sea válido",
            "auth_failed": "Elimina token.json y vuelve a autenticar",
            "api_not_enabled": "Habilita Gmail API en Google Cloud Console"
        }
    }


@router.post("/process-invoices/sync")
async def process_invoices_sync(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Procesar correos de Gmail para extraer facturas de forma síncrona.
    
    Args:
        limit: Número máximo de correos a procesar
        
    Returns:
        Lista de facturas procesadas
    """
    try:
        # Usar la función original de procesamiento que no requiere autenticación
        processed_invoices = process_gmail_invoices(db, limit)
        
        return {
            "message": f"Procesamiento completado. {len(processed_invoices)} facturas procesadas",
            "processed_invoices": processed_invoices,
            "total_processed": len(processed_invoices)
        }
    except Exception as e:
        logger.error(f"Error procesando facturas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando facturas: {str(e)}"
        )


@router.get("/debug/emails")
async def debug_emails(
    limit: int = 10,
    query: str = "has:attachment newer_than:7d"
):
    """
    Endpoint de debug para ver qué correos encuentra Gmail.
    
    Args:
        limit: Número máximo de correos a mostrar
        query: Query de búsqueda de Gmail
        
    Returns:
        Lista de correos encontrados con detalles
    """
    try:
        from src.services.gmail_service_robust import RobustGmailService
        
        gmail_service = RobustGmailService()
        
        # Autenticar con Gmail
        auth_result = gmail_service.authenticate()
        if not auth_result.get('success', False):
            return {"error": f"No se pudo autenticar con Gmail API: {auth_result.get('error_message', 'Error desconocido')}"}
        
        # Buscar correos
        result = gmail_service.search_emails_safe(query=query, max_results=limit)
        emails = result.get('emails', [])
        
        # Preparar datos para debug
        debug_emails = []
        for email in emails:
            debug_email = {
                "id": email.get('id', ''),
                "subject": email.get('subject', ''),
                "from": email.get('from', ''),
                "date": email.get('date', ''),
                "has_attachments": len(email.get('attachments', [])) > 0,
                "attachments_count": len(email.get('attachments', [])),
                "attachments_types": [att.get('mime_type', '') for att in email.get('attachments', [])],
                "body_preview": email.get('body', '')[:200] + "..." if len(email.get('body', '')) > 200 else email.get('body', '')
            }
            debug_emails.append(debug_email)
        
        return {
            "query_used": query,
            "total_emails_found": len(emails),
            "emails": debug_emails
        }
        
    except Exception as e:
        logger.error(f"Error en debug de emails: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en debug de emails: {str(e)}"
        )


@router.get("/debug/invoice-detection")
async def debug_invoice_detection(
    limit: int = 10,
    query: str = "has:attachment newer_than:7d"
):
    """
    Endpoint de debug para probar la detección de facturas.
    """
    try:
        gmail_service = RobustGmailService()
        
        # Autenticar con Gmail
        auth_result = gmail_service.authenticate()
        if not auth_result.get('success', False):
            return {"error": f"No se pudo autenticar con Gmail API: {auth_result.get('error_message', 'Error desconocido')}"}
        
        # Buscar correos
        result = gmail_service.search_emails_safe(query=query, max_results=limit)
        emails = result.get('emails', [])
        
        # Importar el procesador de facturas
        from src.services.gmail_service import InvoiceEmailProcessor
        processor = InvoiceEmailProcessor(None)
        
        # Probar detección en cada correo
        debug_results = []
        for email in emails:
            debug_result = {
                "id": email.get('id', ''),
                "subject": email.get('subject', ''),
                "from": email.get('from', ''),
                "has_attachments": len(email.get('attachments', [])) > 0,
                "attachments_types": [att.get('mime_type', '') for att in email.get('attachments', [])],
                "is_invoice": False,
                "has_invoice_pattern": False,
                "provider": "N/A",
                "detection_details": {}
            }
            
            try:
                # Probar detección de patrón
                debug_result["has_invoice_pattern"] = processor._has_invoice_pattern(email.get('subject', ''))
                
                # Probar detección completa
                debug_result["is_invoice"] = processor.is_invoice_email(email)
                
                # Probar extracción de proveedor
                if debug_result["is_invoice"]:
                    debug_result["provider"] = processor._extract_provider_from_subject(email.get('subject', ''))
                
                # Detalles de detección
                debug_result["detection_details"] = {
                    "subject_lower": email.get('subject', '').lower(),
                    "has_keywords": any(keyword in email.get('subject', '').lower() or keyword in email.get('body', '').lower() 
                                      for keyword in ['factura', 'invoice', 'recibo', 'comprobante', 'gasto', 'expense', 'pago', 'payment', 'cobro', 'charge', 'servicio', 'service', 'bill', 'billing', 'cuenta', 'account']),
                    "has_attachments_check": any(att.get('mime_type', '') in ['application/pdf', 'image/jpeg', 'image/png', 'application/zip', 'application/octet-stream'] 
                                               for att in email.get('attachments', [])),
                    "attachment_types": [att.get('mime_type', '') for att in email.get('attachments', [])]
                }
                
            except Exception as e:
                debug_result["detection_error"] = str(e)
            
            debug_results.append(debug_result)
        
        return {
            "query_used": query,
            "total_emails_found": len(emails),
            "invoice_detection_results": debug_results
        }
        
    except Exception as e:
        logger.error(f"Error en debug de detección de facturas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en debug de detección de facturas: {str(e)}"
        )


@router.get("/debug/processing")
async def debug_processing(
    limit: int = 3,
    query: str = "has:attachment newer_than:7d"
):
    """
    Endpoint de debug para probar el procesamiento completo de facturas.
    """
    try:
        gmail_service = RobustGmailService()
        
        # Autenticar con Gmail
        auth_result = gmail_service.authenticate()
        if not auth_result.get('success', False):
            return {"error": f"No se pudo autenticar con Gmail API: {auth_result.get('error_message', 'Error desconocido')}"}
        
        # Buscar correos recientes con adjuntos
        emails_result = gmail_service.search_emails_safe(query=query, max_results=limit)
        emails = emails_result.get('emails', [])
        
        # Importar el procesador de facturas
        from src.services.gmail_service import InvoiceEmailProcessor
        processor = InvoiceEmailProcessor(None)
        
        debug_results = []
        for email_data in emails:
            debug_result = {
                "id": email_data.get('id', ''),
                "subject": email_data.get('subject', ''),
                "from": email_data.get('from', ''),
                "has_attachments": len(email_data.get('attachments', [])) > 0,
                "attachments_types": [att.get('mime_type', '') for att in email_data.get('attachments', [])],
                "is_invoice": False,
                "invoice_data": None,
                "processing_errors": []
            }
            
            try:
                # Verificar si es una factura
                debug_result["is_invoice"] = processor.is_invoice_email(email_data)
                
                if debug_result["is_invoice"]:
                    # Extraer datos de la factura
                    invoice_data = processor.extract_invoice_data(email_data)
                    debug_result["invoice_data"] = {
                        "provider": invoice_data.get('provider', ''),
                        "amount": invoice_data.get('amount', 0),
                        "date": str(invoice_data.get('date', '')),
                        "description": invoice_data.get('description', ''),
                        "email_subject": invoice_data.get('email_subject', ''),
                        "email_from": invoice_data.get('email_from', ''),
                        "attachments_count": len(invoice_data.get('attachments', []))
                    }
                    
                    # Intentar crear factura en la base de datos (sin guardar)
                    from src.services.gmail_service import create_invoice_from_email
                    from src.database import get_db
                    
                    # Simular la creación sin guardar
                    try:
                        # Crear una sesión de prueba
                        db = next(get_db())
                        invoice = create_invoice_from_email(db, invoice_data)
                        if invoice:
                            debug_result["invoice_creation"] = {
                                "success": True,
                                "invoice_id": invoice.id,
                                "provider": invoice.provider,
                                "amount": invoice.amount
                            }
                        else:
                            debug_result["invoice_creation"] = {
                                "success": False,
                                "error": "create_invoice_from_email returned None"
                            }
                    except Exception as e:
                        debug_result["invoice_creation"] = {
                            "success": False,
                            "error": str(e)
                        }
                        debug_result["processing_errors"].append(f"Error creando factura: {str(e)}")
                
            except Exception as e:
                debug_result["processing_errors"].append(f"Error general: {str(e)}")
            
            debug_results.append(debug_result)
        
        return {
            "query_used": query,
            "total_emails_found": len(emails),
            "processing_results": debug_results
        }
        
    except Exception as e:
        logger.error(f"Error en debug de procesamiento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en debug de procesamiento: {str(e)}"
        )


@router.get("/analyze-invoices")
async def analyze_invoices_for_upload(
    query: str = Query(default="has:attachment newer_than:30d", description="Query de búsqueda de Gmail"),
    max_results: int = Query(default=50, ge=1, le=100, description="Número máximo de resultados")
):
    """
    Analizar correos de Gmail para identificar facturas que deben subirse al sistema.
    
    Args:
        query: Query de búsqueda de Gmail
        max_results: Número máximo de correos a analizar
        
    Returns:
        Dict con facturas identificadas para subir, categorizadas por usuario
    """
    try:
        from src.services.gmail_service import InvoiceEmailProcessor
        from src.database import get_db
        from src.models import Invoice
        
        # Obtener servicio Gmail
        gmail_service = RobustGmailService()
        auth_result = gmail_service.authenticate()
        
        if not auth_result.get('success', False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"No se pudo autenticar con Gmail API: {auth_result.get('error_message', 'Error desconocido')}"
            )
        
        # Buscar correos
        search_result = gmail_service.search_emails_safe(query, max_results)
        if not search_result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=search_result['error_message']
            )
        
        emails = search_result['emails']
        
        # Procesar correos para identificar facturas
        processor = InvoiceEmailProcessor(None)
        db = next(get_db())
        
        invoices_to_upload = []
        invoices_without_user = []
        already_uploaded = []
        
        for email_data in emails:
            try:
                # Verificar si es una factura
                if not processor.is_invoice_email(email_data):
                    continue
                
                # Extraer datos de la factura
                invoice_data = processor.extract_invoice_data(email_data)
                
                # Verificar si ya existe en la base de datos
                existing_invoice = db.query(Invoice).filter(
                    Invoice.provider == invoice_data['provider'],
                    Invoice.amount == invoice_data['amount'],
                    Invoice.date == invoice_data['date']
                ).first()
                
                if existing_invoice:
                    already_uploaded.append({
                        'email_id': email_data.get('id', ''),
                        'email_subject': email_data.get('subject', ''),
                        'provider': invoice_data['provider'],
                        'amount': invoice_data['amount'],
                        'date': str(invoice_data['date']),
                        'existing_invoice_id': existing_invoice.id,
                        'existing_user': existing_invoice.user.name if existing_invoice.user else 'Usuario desconocido'
                    })
                    continue
                
                # Intentar identificar el usuario por email del remitente
                sender_email = email_data.get('from', '').lower()
                user = None
                
                # Buscar usuario por dominio del email o email completo
                if '@' in sender_email:
                    domain = sender_email.split('@')[1]
                    # Aquí podrías implementar lógica para mapear dominios a usuarios específicos
                    # Por ahora, marcaremos como sin usuario
                
                invoice_info = {
                    'email_id': email_data.get('id', ''),
                    'email_subject': email_data.get('subject', ''),
                    'email_from': email_data.get('from', ''),
                    'provider': invoice_data['provider'],
                    'amount': invoice_data['amount'],
                    'date': str(invoice_data['date']),
                    'description': invoice_data['description'],
                    'attachments': email_data.get('attachments', []),
                    'raw_invoice_data': invoice_data
                }
                
                if user:
                    invoice_info['suggested_user_id'] = user.id
                    invoice_info['suggested_user_name'] = user.name
                    invoices_to_upload.append(invoice_info)
                else:
                    invoice_info['reason_no_user'] = 'No se pudo identificar usuario por email del remitente'
                    invoices_without_user.append(invoice_info)
                    
            except Exception as e:
                logger.error(f"Error procesando email {email_data.get('id', 'unknown')}: {str(e)}")
                continue
        
        return {
            "success": True,
            "summary": {
                "total_emails_analyzed": len(emails),
                "invoices_found": len(invoices_to_upload) + len(invoices_without_user),
                "invoices_with_user": len(invoices_to_upload),
                "invoices_without_user": len(invoices_without_user),
                "already_uploaded": len(already_uploaded)
            },
            "invoices_to_upload": invoices_to_upload,
            "invoices_without_user": invoices_without_user,
            "already_uploaded": already_uploaded,
            "query_used": query,
            "analysis_date": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analizando facturas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analizando facturas: {str(e)}"
        )


@router.post("/migrate-to-secret-manager")
async def migrate_to_secret_manager():
    """
    Migrar credenciales y token de Gmail a Secret Manager.
    
    Returns:
        Resultado de la migración
    """
    try:
        from src.services.secret_manager import secret_manager_service
        
        # Verificar si Secret Manager está disponible
        if not secret_manager_service.is_available():
            return {
                "success": False,
                "error": "Secret Manager no está disponible. Verifica la configuración de Google Cloud."
            }
        
        results = {
            "credentials_migrated": False,
            "token_migrated": False,
            "errors": []
        }
        
        # Migrar credenciales
        credentials_path = '/app/credentials.json'
        if os.path.exists(credentials_path):
            try:
                with open(credentials_path, 'r') as f:
                    credentials_data = f.read()
                
                success = secret_manager_service.store_secret(
                    "gmail-oauth-credentials",
                    credentials_data,
                    "gmail-oauth-credentials"
                )
                
                if success:
                    results["credentials_migrated"] = True
                    logger.info("Credenciales migradas a Secret Manager")
                else:
                    results["errors"].append("Error migrando credenciales")
                    
            except Exception as e:
                results["errors"].append(f"Error leyendo credentials.json: {str(e)}")
        else:
            results["errors"].append("Archivo credentials.json no encontrado")
        
        # Migrar token
        token_path = '/app/token.json'
        if os.path.exists(token_path):
            try:
                with open(token_path, 'r') as f:
                    token_data = f.read()
                
                success = secret_manager_service.store_secret(
                    "gmail-oauth-token",
                    token_data,
                    "gmail-oauth-token"
                )
                
                if success:
                    results["token_migrated"] = True
                    logger.info("Token migrado a Secret Manager")
                else:
                    results["errors"].append("Error migrando token")
                    
            except Exception as e:
                results["errors"].append(f"Error leyendo token.json: {str(e)}")
        else:
            logger.info("Archivo token.json no encontrado (esto es normal)")
        
        # Determinar éxito general
        results["success"] = results["credentials_migrated"] and len(results["errors"]) == 0
        
        if results["success"]:
            results["message"] = "Migración completada exitosamente"
        else:
            results["message"] = "Migración completada con errores"
        
        return results
        
    except Exception as e:
        logger.error(f"Error en migración a Secret Manager: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en migración a Secret Manager: {str(e)}"
        )
