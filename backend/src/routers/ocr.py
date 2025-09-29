"""
Router para endpoints de OCR.
Proporciona funcionalidades para procesamiento OCR de facturas físicas.
"""

import os
import tempfile
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import logging

from src.database import get_db
from src.services.ocr_service import ocr_service
from src.models import Invoice, User, InvoiceStatus, ExpenseCategory, PaymentMethod
from src.schemas import InvoiceCreate, Invoice
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ocr", tags=["ocr"])


@router.post("/process", response_model=Dict[str, Any])
async def process_invoice_ocr(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """
    Procesar una factura física usando OCR.
    
    Args:
        file: Archivo de factura (imagen o PDF)
        user_id: ID del usuario que sube la factura
        db: Sesión de base de datos
        
    Returns:
        Dict con los datos extraídos por OCR
        
    Raises:
        HTTPException: Si hay error en el procesamiento
    """
    try:
        # Verificar que el usuario existe
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Verificar formato de archivo
        if not ocr_service.is_supported_format(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formato de archivo no soportado. Formatos permitidos: {', '.join(ocr_service.supported_formats)}"
            )
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Procesar archivo con OCR
            ocr_result = ocr_service.process_invoice_file(temp_file_path)
            
            # Agregar información del usuario
            ocr_result['user_id'] = user_id
            ocr_result['user_name'] = user.name
            
            logger.info(f"OCR procesado exitosamente para usuario {user_id}")
            return ocr_result
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando OCR: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando factura con OCR: {str(e)}"
        )


@router.post("/process-and-create", response_model=Invoice)
async def process_and_create_invoice(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    payment_method: PaymentMethod = Form(...),
    category: ExpenseCategory = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Procesar una factura con OCR y crear el registro en la base de datos.
    
    Args:
        file: Archivo de factura (imagen o PDF)
        user_id: ID del usuario
        payment_method: Método de pago
        category: Categoría del gasto
        description: Descripción opcional
        db: Sesión de base de datos
        
    Returns:
        InvoiceResponse: Factura creada
        
    Raises:
        HTTPException: Si hay error en el procesamiento o creación
    """
    try:
        # Verificar que el usuario existe
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Verificar formato de archivo
        if not ocr_service.is_supported_format(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formato de archivo no soportado. Formatos permitidos: {', '.join(ocr_service.supported_formats)}"
            )
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Procesar archivo con OCR
            ocr_result = ocr_service.process_invoice_file(temp_file_path)
            
            # Validar que se extrajo al menos el monto
            if not ocr_result.get('amount'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se pudo extraer el monto de la factura. Verifique que la imagen sea clara y contenga información legible."
                )
            
            # Crear nombre único para el archivo
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}_{file.filename}"
            file_path = os.path.join("uploads", unique_filename)
            
            # Crear directorio si no existe
            os.makedirs("uploads", exist_ok=True)
            
            # Copiar archivo a la ubicación final
            with open(file_path, "wb") as final_file:
                final_file.write(content)
            
            # Crear factura en la base de datos
            invoice_data = InvoiceCreate(
                date=datetime.fromisoformat(ocr_result['date']) if ocr_result.get('date') else datetime.now(),
                provider=ocr_result.get('provider', 'Proveedor no identificado'),
                amount=ocr_result['amount'],
                payment_method=payment_method,
                category=category,
                user_id=user_id,
                description=description or f"Factura procesada con OCR. Confianza: {ocr_result['confidence']:.2f}",
                file_path=file_path
            )
            
            # Crear registro en la base de datos
            db_invoice = Invoice(
                date=invoice_data.date,
                provider=invoice_data.provider,
                amount=invoice_data.amount,
                payment_method=invoice_data.payment_method,
                category=invoice_data.category,
                user_id=invoice_data.user_id,
                description=invoice_data.description,
                file_path=invoice_data.file_path,
                status=InvoiceStatus.PENDING,
                ocr_data=ocr_result,  # Guardar datos OCR para referencia
                ocr_confidence=ocr_result['confidence']
            )
            
            db.add(db_invoice)
            db.commit()
            db.refresh(db_invoice)
            
            logger.info(f"Factura creada con OCR: ID {db_invoice.id}, confianza {ocr_result['confidence']:.2f}")
            
            return Invoice.from_orm(db_invoice)
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando y creando factura con OCR: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando factura con OCR: {str(e)}"
        )


@router.get("/supported-formats")
async def get_supported_formats():
    """
    Obtener lista de formatos de archivo soportados para OCR.
    
    Returns:
        Dict con los formatos soportados
    """
    return {
        "supported_formats": ocr_service.supported_formats,
        "description": "Formatos de archivo soportados para procesamiento OCR"
    }


@router.get("/invoice/{invoice_id}/ocr-data")
async def get_invoice_ocr_data(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener datos OCR de una factura específica.
    
    Args:
        invoice_id: ID de la factura
        db: Sesión de base de datos
        
    Returns:
        Dict con los datos OCR de la factura
        
    Raises:
        HTTPException: Si la factura no existe o no tiene datos OCR
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura no encontrada"
        )
    
    if not hasattr(invoice, 'ocr_data') or not invoice.ocr_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Esta factura no tiene datos OCR asociados"
        )
    
    return {
        "invoice_id": invoice_id,
        "ocr_data": invoice.ocr_data,
        "ocr_confidence": getattr(invoice, 'ocr_confidence', None),
        "processed_at": invoice.created_at.isoformat() if hasattr(invoice, 'created_at') else None
    }


@router.post("/validate-extraction")
async def validate_ocr_extraction(
    ocr_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Validar y corregir datos extraídos por OCR.
    
    Args:
        ocr_data: Datos extraídos por OCR con posibles correcciones
        db: Sesión de base de datos
        
    Returns:
        Dict con los datos validados
    """
    try:
        # Validar estructura básica
        required_fields = ['amount', 'user_id']
        for field in required_fields:
            if field not in ocr_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Campo requerido faltante: {field}"
                )
        
        # Validar monto
        try:
            amount = float(ocr_data['amount'])
            if amount <= 0:
                raise ValueError("El monto debe ser mayor a 0")
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Monto inválido"
            )
        
        # Validar usuario
        user = db.query(User).filter(User.id == ocr_data['user_id']).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Validar fecha si está presente
        if ocr_data.get('date'):
            try:
                datetime.fromisoformat(ocr_data['date'])
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato de fecha inválido"
                )
        
        # Calcular nueva confianza
        confidence = ocr_service._calculate_confidence(ocr_data)
        ocr_data['confidence'] = confidence
        
        return {
            "validated_data": ocr_data,
            "is_valid": True,
            "confidence": confidence
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validando datos OCR: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validando datos OCR: {str(e)}"
        )
