"""
Router robusto para endpoints de integración con Gmail API.
Maneja la sincronización y procesamiento de correos electrónicos con mejor manejo de errores.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
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
