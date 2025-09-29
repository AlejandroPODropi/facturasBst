"""
Router para endpoints de integración con Gmail API.
Maneja la sincronización y procesamiento de correos electrónicos.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging

from src.database import get_db
from src.services.gmail_service import GmailService, process_gmail_invoices
from src.schemas import MessageResponse

router = APIRouter(prefix="/gmail", tags=["gmail"])

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/auth/status")
async def get_auth_status():
    """
    Verificar estado de autenticación con Gmail API.
    
    Returns:
        Dict con estado de autenticación
    """
    try:
        gmail_service = GmailService()
        is_authenticated = gmail_service.authenticate()
        
        return {
            "authenticated": is_authenticated,
            "message": "Autenticado con Gmail API" if is_authenticated else "No autenticado"
        }
    except Exception as e:
        logger.error(f"Error verificando autenticación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verificando autenticación: {str(e)}"
        )


@router.post("/auth/authenticate")
async def authenticate_gmail():
    """
    Iniciar proceso de autenticación con Gmail API.
    
    Returns:
        Dict con resultado de autenticación
    """
    try:
        gmail_service = GmailService()
        is_authenticated = gmail_service.authenticate()
        
        if is_authenticated:
            return {
                "success": True,
                "message": "Autenticación exitosa con Gmail API"
            }
        else:
            return {
                "success": False,
                "message": "Error en la autenticación con Gmail API"
            }
    except Exception as e:
        logger.error(f"Error en autenticación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en autenticación: {str(e)}"
        )


@router.get("/emails/search")
async def search_emails(
    query: str = "has:attachment newer_than:7d",
    max_results: int = 10,
    db: Session = Depends(get_db)
):
    """
    Buscar correos electrónicos con criterios específicos.
    
    Args:
        query: Query de búsqueda de Gmail
        max_results: Número máximo de resultados
        
    Returns:
        Lista de correos encontrados
    """
    try:
        gmail_service = GmailService()
        
        if not gmail_service.authenticate():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudo autenticar con Gmail API"
            )
        
        emails = gmail_service.search_emails(query, max_results)
        
        return {
            "emails": emails,
            "total": len(emails),
            "query": query
        }
    except Exception as e:
        logger.error(f"Error buscando correos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error buscando correos: {str(e)}"
        )


@router.get("/emails/{message_id}")
async def get_email_details(
    message_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtener detalles de un correo específico.
    
    Args:
        message_id: ID del mensaje
        
    Returns:
        Detalles del correo
    """
    try:
        gmail_service = GmailService()
        
        if not gmail_service.authenticate():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudo autenticar con Gmail API"
            )
        
        email_data = gmail_service.get_email_details(message_id)
        
        if not email_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Correo no encontrado"
            )
        
        return email_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo detalles del correo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo detalles del correo: {str(e)}"
        )


@router.post("/process-invoices")
async def process_invoices_from_gmail(
    background_tasks: BackgroundTasks,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Procesar correos de Gmail para extraer facturas automáticamente.
    
    Args:
        limit: Número máximo de correos a procesar
        
    Returns:
        Resultado del procesamiento
    """
    try:
        # Ejecutar procesamiento en background
        background_tasks.add_task(process_gmail_invoices, db, limit)
        
        return {
            "message": "Procesamiento de facturas iniciado en background",
            "limit": limit,
            "status": "processing"
        }
    except Exception as e:
        logger.error(f"Error iniciando procesamiento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error iniciando procesamiento: {str(e)}"
        )


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


@router.get("/attachments/{message_id}/{attachment_id}")
async def download_attachment(
    message_id: str,
    attachment_id: str,
    db: Session = Depends(get_db)
):
    """
    Descargar un archivo adjunto de un correo.
    
    Args:
        message_id: ID del mensaje
        attachment_id: ID del adjunto
        
    Returns:
        Archivo adjunto
    """
    try:
        gmail_service = GmailService()
        
        if not gmail_service.authenticate():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudo autenticar con Gmail API"
            )
        
        attachment_data = gmail_service.download_attachment(message_id, attachment_id)
        
        if not attachment_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Adjunto no encontrado"
            )
        
        return {
            "data": attachment_data,
            "size": len(attachment_data)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error descargando adjunto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error descargando adjunto: {str(e)}"
        )


@router.post("/emails/{message_id}/mark-read")
async def mark_email_as_read(
    message_id: str,
    db: Session = Depends(get_db)
):
    """
    Marcar un correo como leído.
    
    Args:
        message_id: ID del mensaje
        
    Returns:
        Resultado de la operación
    """
    try:
        gmail_service = GmailService()
        
        if not gmail_service.authenticate():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudo autenticar con Gmail API"
            )
        
        success = gmail_service.mark_as_read(message_id)
        
        if success:
            return {
                "message": "Correo marcado como leído",
                "message_id": message_id
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error marcando correo como leído"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marcando correo como leído: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marcando correo como leído: {str(e)}"
        )


@router.get("/stats")
async def get_gmail_stats(db: Session = Depends(get_db)):
    """
    Obtener estadísticas de la integración con Gmail.
    
    Returns:
        Estadísticas de Gmail
    """
    try:
        gmail_service = GmailService()
        
        if not gmail_service.authenticate():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudo autenticar con Gmail API"
            )
        
        # Buscar correos recientes
        recent_emails = gmail_service.search_emails(
            query="newer_than:7d",
            max_results=100
        )
        
        # Buscar correos con adjuntos
        emails_with_attachments = gmail_service.search_emails(
            query="has:attachment newer_than:7d",
            max_results=100
        )
        
        # Buscar correos no leídos
        unread_emails = gmail_service.search_emails(
            query="is:unread newer_than:7d",
            max_results=100
        )
        
        return {
            "total_emails_7d": len(recent_emails),
            "emails_with_attachments_7d": len(emails_with_attachments),
            "unread_emails_7d": len(unread_emails),
            "attachment_rate": len(emails_with_attachments) / len(recent_emails) * 100 if recent_emails else 0
        }
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )
