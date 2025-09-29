"""
Router para endpoints de facturas.
Maneja la carga, consulta, actualización y exportación de facturas.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
import os
import uuid
from datetime import datetime

from src.database import get_db, settings
from src.models import Invoice, User, InvoiceStatus, ExpenseCategory, PaymentMethod
from src.schemas import (
    InvoiceCreate, InvoiceUpdate, Invoice as InvoiceSchema, 
    InvoiceFilters, PaginatedResponse, ExportParams, MessageResponse
)
from src.services.excel_export import export_invoices_to_excel

router = APIRouter()


@router.post("/upload", response_model=InvoiceSchema, status_code=status.HTTP_201_CREATED)
async def upload_invoice(
    date: datetime = Form(...),
    provider: str = Form(...),
    amount: float = Form(...),
    payment_method: PaymentMethod = Form(...),
    category: ExpenseCategory = Form(...),
    user_id: int = Form(...),
    description: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Registrar una nueva factura en el sistema.
    
    Args:
        date: Fecha de la factura
        provider: Nombre del proveedor
        amount: Monto de la factura
        payment_method: Método de pago
        category: Categoría del gasto
        user_id: ID del usuario que registra la factura
        description: Descripción adicional (opcional)
        file: Archivo adjunto (opcional)
        db: Sesión de base de datos
        
    Returns:
        InvoiceSchema: Factura creada
        
    Raises:
        HTTPException: Si el usuario no existe, el monto es inválido o hay error con el archivo
    """
    # Validar que el usuario existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Validar monto
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El monto debe ser mayor a 0"
        )
    
    # Manejar archivo adjunto si se proporciona
    file_path = None
    if file:
        # Validar tipo de archivo
        allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.xlsx', '.xls'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de archivo no permitido. Use PDF, JPG, PNG o Excel"
            )
        
        # Validar tamaño del archivo
        file_content = await file.read()
        if len(file_content) > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El archivo es demasiado grande. Máximo {settings.max_file_size} bytes"
            )
        
        # Generar nombre único para el archivo
        file_id = str(uuid.uuid4())
        file_path = f"{settings.upload_dir}/{file_id}{file_extension}"
        
        # Guardar archivo
        os.makedirs(settings.upload_dir, exist_ok=True)
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
    
    # Crear factura
    invoice_data = InvoiceCreate(
        user_id=user_id,
        date=date,
        provider=provider,
        amount=amount,
        payment_method=payment_method,
        category=category,
        description=description
    )
    
    db_invoice = Invoice(**invoice_data.dict(), file_path=file_path)
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    
    return db_invoice


@router.get("/", response_model=PaginatedResponse)
async def get_invoices(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    user_id: Optional[int] = Query(None, description="Filtrar por usuario"),
    status: Optional[InvoiceStatus] = Query(None, description="Filtrar por estado"),
    category: Optional[ExpenseCategory] = Query(None, description="Filtrar por categoría"),
    payment_method: Optional[PaymentMethod] = Query(None, description="Filtrar por método de pago"),
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    provider: Optional[str] = Query(None, description="Filtrar por proveedor"),
    search_text: Optional[str] = Query(None, description="Búsqueda por texto en proveedor o descripción"),
    db: Session = Depends(get_db)
):
    """
    Obtener facturas con filtros y paginación.
    
    Args:
        page: Número de página
        size: Tamaño de página
        user_id: Filtrar por usuario
        status: Filtrar por estado
        category: Filtrar por categoría
        payment_method: Filtrar por método de pago
        start_date: Fecha de inicio
        end_date: Fecha de fin
        provider: Filtrar por proveedor
        db: Sesión de base de datos
        
    Returns:
        PaginatedResponse: Facturas paginadas
    """
    # Construir query base
    query = db.query(Invoice)
    
    # Aplicar filtros
    if user_id:
        query = query.filter(Invoice.user_id == user_id)
    if status:
        query = query.filter(Invoice.status == status)
    if category:
        query = query.filter(Invoice.category == category)
    if payment_method:
        query = query.filter(Invoice.payment_method == payment_method)
    if start_date:
        query = query.filter(Invoice.date >= start_date)
    if end_date:
        query = query.filter(Invoice.date <= end_date)
    if provider:
        query = query.filter(Invoice.provider.ilike(f"%{provider}%"))
    if search_text:
        # Búsqueda por texto en proveedor o descripción
        search_filter = f"%{search_text}%"
        query = query.filter(
            (Invoice.provider.ilike(search_filter)) |
            (Invoice.description.ilike(search_filter))
        )
    
    # Contar total de registros
    total = query.count()
    
    # Aplicar paginación
    offset = (page - 1) * size
    invoices = query.offset(offset).limit(size).all()
    
    # Calcular número de páginas
    pages = (total + size - 1) // size
    
    return PaginatedResponse(
        items=invoices,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{invoice_id}", response_model=InvoiceSchema)
async def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """
    Obtener una factura específica por ID.
    
    Args:
        invoice_id: ID de la factura
        db: Sesión de base de datos
        
    Returns:
        InvoiceSchema: Factura encontrada
        
    Raises:
        HTTPException: Si la factura no existe
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura no encontrada"
        )
    return invoice


@router.put("/{invoice_id}", response_model=InvoiceSchema)
async def update_invoice(
    invoice_id: int,
    invoice_update: InvoiceUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar una factura existente.
    
    Args:
        invoice_id: ID de la factura a actualizar
        invoice_update: Datos a actualizar
        db: Sesión de base de datos
        
    Returns:
        InvoiceSchema: Factura actualizada
        
    Raises:
        HTTPException: Si la factura no existe o el monto es inválido
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura no encontrada"
        )
    
    # Validar monto si se está actualizando
    if invoice_update.amount is not None and invoice_update.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El monto debe ser mayor a 0"
        )
    
    # Actualizar campos
    update_data = invoice_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(invoice, field, value)
    
    db.commit()
    db.refresh(invoice)
    
    return invoice


@router.get("/export/excel")
async def export_invoices_excel(
    user_id: Optional[int] = Query(None, description="Filtrar por usuario"),
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    status: Optional[InvoiceStatus] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db)
):
    """
    Exportar facturas a archivo Excel.
    
    Args:
        user_id: Filtrar por usuario
        start_date: Fecha de inicio
        end_date: Fecha de fin
        status: Filtrar por estado
        db: Sesión de base de datos
        
    Returns:
        FileResponse: Archivo Excel con las facturas
        
    Raises:
        HTTPException: Si no hay facturas para exportar
    """
    # Construir query con filtros
    query = db.query(Invoice)
    
    if user_id:
        query = query.filter(Invoice.user_id == user_id)
    if start_date:
        query = query.filter(Invoice.date >= start_date)
    if end_date:
        query = query.filter(Invoice.date <= end_date)
    if status:
        query = query.filter(Invoice.status == status)
    
    invoices = query.all()
    
    if not invoices:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay facturas para exportar con los filtros especificados"
        )
    
    # Generar archivo Excel
    file_path = export_invoices_to_excel(invoices)
    
    return {
        "message": "Archivo Excel generado exitosamente",
        "file_path": file_path,
        "total_invoices": len(invoices)
    }


@router.patch("/{invoice_id}/validate", response_model=InvoiceSchema)
async def validate_invoice(
    invoice_id: int,
    new_status: InvoiceStatus = Form(...),
    validation_notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Validar o rechazar una factura.
    
    Args:
        invoice_id: ID de la factura a validar
        new_status: Nuevo estado (validada o rechazada)
        validation_notes: Notas de validación (opcional)
        db: Sesión de base de datos
        
    Returns:
        InvoiceSchema: Factura actualizada
        
    Raises:
        HTTPException: Si la factura no existe o el estado es inválido
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura no encontrada"
        )
    
    # Validar que el nuevo estado sea válido para validación
    if new_status not in [InvoiceStatus.VALIDATED, InvoiceStatus.REJECTED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado inválido. Solo se puede validar o rechazar facturas"
        )
    
    # Actualizar estado y notas
    invoice.status = new_status
    if validation_notes:
        # Agregar notas a la descripción existente
        if invoice.description:
            invoice.description += f"\n\nNotas de validación: {validation_notes}"
        else:
            invoice.description = f"Notas de validación: {validation_notes}"
    
    db.commit()
    db.refresh(invoice)
    
    return invoice


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """
    Eliminar una factura del sistema.
    
    Args:
        invoice_id: ID de la factura a eliminar
        db: Sesión de base de datos
        
    Raises:
        HTTPException: Si la factura no existe
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura no encontrada"
        )
    
    # Eliminar archivo adjunto si existe
    if invoice.file_path and os.path.exists(invoice.file_path):
        os.remove(invoice.file_path)
    
    db.delete(invoice)
    db.commit()


@router.get("/{invoice_id}/download")
async def download_invoice_file(invoice_id: int, db: Session = Depends(get_db)):
    """
    Descargar archivo adjunto de una factura.
    
    Args:
        invoice_id: ID de la factura
        db: Sesión de base de datos
        
    Returns:
        FileResponse: Archivo adjunto
        
    Raises:
        HTTPException: Si la factura no existe o no tiene archivo
    """
    # Buscar la factura
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura no encontrada"
        )
    
    # Verificar que la factura tenga archivo adjunto
    if not invoice.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Esta factura no tiene archivo adjunto"
        )
    
    # Verificar que el archivo exista en el sistema de archivos
    if not os.path.exists(invoice.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El archivo adjunto no se encuentra en el servidor"
        )
    
    # Obtener el nombre del archivo original
    filename = os.path.basename(invoice.file_path)
    
    # Determinar el tipo de contenido basado en la extensión
    file_extension = os.path.splitext(filename)[1].lower()
    media_type_map = {
        '.pdf': 'application/pdf',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.xls': 'application/vnd.ms-excel',
        '.csv': 'text/csv'
    }
    
    media_type = media_type_map.get(file_extension, 'application/octet-stream')
    
    # Generar nombre de archivo para descarga
    download_filename = f"factura_{invoice_id}_{filename}"
    
    return FileResponse(
        path=invoice.file_path,
        filename=download_filename,
        media_type=media_type
    )
