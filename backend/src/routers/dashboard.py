"""
Router para endpoints del dashboard.
Proporciona estadísticas y métricas para el dashboard principal.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from src.database import get_db
from src.services.dashboard_stats import get_dashboard_stats

router = APIRouter(tags=["dashboard"])


@router.get("/stats", response_model=Dict[str, Any])
async def get_dashboard_statistics(db: Session = Depends(get_db)):
    """
    Obtener estadísticas completas del dashboard.
    
    Incluye:
    - Estadísticas básicas (usuarios, facturas, montos)
    - Tendencias mensuales
    - Estadísticas por usuario
    - Distribución por categorías
    - Distribución por métodos de pago
    - Rendimiento de validación
    - Actividad reciente
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Dict con todas las estadísticas del dashboard
        
    Raises:
        HTTPException: Si hay error al obtener las estadísticas
    """
    try:
        stats = get_dashboard_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas del dashboard: {str(e)}"
        )


@router.get("/basic-stats", response_model=Dict[str, Any])
async def get_basic_statistics(db: Session = Depends(get_db)):
    """
    Obtener solo las estadísticas básicas del dashboard.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Dict con estadísticas básicas
    """
    try:
        from src.services.dashboard_stats import DashboardStatsService
        service = DashboardStatsService(db)
        return service.get_basic_stats()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas básicas: {str(e)}"
        )


@router.get("/trends", response_model=Dict[str, Any])
async def get_monthly_trends(months: int = 6, db: Session = Depends(get_db)):
    """
    Obtener tendencias mensuales de facturas.
    
    Args:
        months: Número de meses a incluir (default: 6)
        db: Sesión de base de datos
        
    Returns:
        Dict con tendencias mensuales
    """
    try:
        from src.services.dashboard_stats import DashboardStatsService
        service = DashboardStatsService(db)
        trends = service.get_monthly_trends(months)
        return {"trends": trends}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tendencias: {str(e)}"
        )


@router.get("/user-stats", response_model=Dict[str, Any])
async def get_user_statistics(limit: int = 10, db: Session = Depends(get_db)):
    """
    Obtener estadísticas por usuario.
    
    Args:
        limit: Número máximo de usuarios a retornar (default: 10)
        db: Sesión de base de datos
        
    Returns:
        Dict con estadísticas por usuario
    """
    try:
        from src.services.dashboard_stats import DashboardStatsService
        service = DashboardStatsService(db)
        user_stats = service.get_user_stats(limit)
        return {"user_stats": user_stats}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas de usuarios: {str(e)}"
        )


@router.get("/category-distribution", response_model=Dict[str, Any])
async def get_category_distribution(db: Session = Depends(get_db)):
    """
    Obtener distribución de facturas por categoría.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Dict con distribución por categoría
    """
    try:
        from src.services.dashboard_stats import DashboardStatsService
        service = DashboardStatsService(db)
        distribution = service.get_category_distribution()
        return {"category_distribution": distribution}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener distribución por categoría: {str(e)}"
        )


@router.get("/payment-method-distribution", response_model=Dict[str, Any])
async def get_payment_method_distribution(db: Session = Depends(get_db)):
    """
    Obtener distribución de facturas por método de pago.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Dict con distribución por método de pago
    """
    try:
        from src.services.dashboard_stats import DashboardStatsService
        service = DashboardStatsService(db)
        distribution = service.get_payment_method_distribution()
        return {"payment_method_distribution": distribution}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener distribución por método de pago: {str(e)}"
        )


@router.get("/validation-performance", response_model=Dict[str, Any])
async def get_validation_performance(db: Session = Depends(get_db)):
    """
    Obtener métricas de rendimiento de validación.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Dict con métricas de validación
    """
    try:
        from src.services.dashboard_stats import DashboardStatsService
        service = DashboardStatsService(db)
        performance = service.get_validation_performance()
        return {"validation_performance": performance}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener métricas de validación: {str(e)}"
        )


@router.get("/recent-activity", response_model=Dict[str, Any])
async def get_recent_activity(limit: int = 10, db: Session = Depends(get_db)):
    """
    Obtener actividad reciente del sistema.
    
    Args:
        limit: Número máximo de actividades a retornar (default: 10)
        db: Sesión de base de datos
        
    Returns:
        Dict con actividad reciente
    """
    try:
        from src.services.dashboard_stats import DashboardStatsService
        service = DashboardStatsService(db)
        activity = service.get_recent_activity(limit)
        return {"recent_activity": activity}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener actividad reciente: {str(e)}"
        )
