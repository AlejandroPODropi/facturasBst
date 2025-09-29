"""
Servicio para calcular estadísticas del dashboard.
Proporciona métricas y datos agregados para el dashboard principal.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
from typing import Dict, List, Any
from datetime import datetime, timedelta
from collections import defaultdict

from src.models import Invoice, User, InvoiceStatus, ExpenseCategory, PaymentMethod


class DashboardStatsService:
    """Servicio para calcular estadísticas del dashboard."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_basic_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas básicas del sistema.
        
        Returns:
            Dict con estadísticas básicas
        """
        # Contar usuarios
        total_users = self.db.query(User).count()
        
        # Contar facturas por estado
        invoices_by_status = self.db.query(
            Invoice.status,
            func.count(Invoice.id).label('count')
        ).group_by(Invoice.status).all()
        
        status_counts = {status.value: count for status, count in invoices_by_status}
        
        # Calcular monto total
        total_amount = self.db.query(func.sum(Invoice.amount)).scalar() or 0
        
        # Calcular monto por estado
        amount_by_status = self.db.query(
            Invoice.status,
            func.sum(Invoice.amount).label('total')
        ).group_by(Invoice.status).all()
        
        amount_by_status_dict = {status.value: total for status, total in amount_by_status}
        
        return {
            'total_users': total_users,
            'total_invoices': sum(status_counts.values()),
            'total_amount': float(total_amount),
            'invoices_by_status': status_counts,
            'amount_by_status': amount_by_status_dict
        }
    
    def get_monthly_trends(self, months: int = 6) -> List[Dict[str, Any]]:
        """
        Obtener tendencias mensuales de facturas.
        
        Args:
            months: Número de meses a incluir
            
        Returns:
            Lista de datos mensuales
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        
        # Obtener facturas por mes
        monthly_data = self.db.query(
            extract('year', Invoice.date).label('year'),
            extract('month', Invoice.date).label('month'),
            func.count(Invoice.id).label('count'),
            func.sum(Invoice.amount).label('total_amount')
        ).filter(
            Invoice.date >= start_date
        ).group_by(
            extract('year', Invoice.date),
            extract('month', Invoice.date)
        ).order_by(
            extract('year', Invoice.date),
            extract('month', Invoice.date)
        ).all()
        
        # Formatear datos
        trends = []
        for year, month, count, total_amount in monthly_data:
            trends.append({
                'year': int(year),
                'month': int(month),
                'month_name': datetime(int(year), int(month), 1).strftime('%B'),
                'count': count,
                'total_amount': float(total_amount or 0)
            })
        
        return trends
    
    def get_user_stats(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtener estadísticas por usuario.
        
        Args:
            limit: Número máximo de usuarios a retornar
            
        Returns:
            Lista de estadísticas por usuario
        """
        user_stats = self.db.query(
            User.id,
            User.name,
            User.email,
            func.count(Invoice.id).label('invoice_count'),
            func.sum(Invoice.amount).label('total_amount'),
            func.avg(Invoice.amount).label('avg_amount')
        ).join(
            Invoice, User.id == Invoice.user_id
        ).group_by(
            User.id, User.name, User.email
        ).order_by(
            func.sum(Invoice.amount).desc()
        ).limit(limit).all()
        
        stats = []
        for user_id, name, email, count, total, avg in user_stats:
            stats.append({
                'user_id': user_id,
                'name': name,
                'email': email,
                'invoice_count': count,
                'total_amount': float(total or 0),
                'avg_amount': float(avg or 0)
            })
        
        return stats
    
    def get_category_distribution(self) -> List[Dict[str, Any]]:
        """
        Obtener distribución de facturas por categoría.
        
        Returns:
            Lista de distribución por categoría
        """
        category_stats = self.db.query(
            Invoice.category,
            func.count(Invoice.id).label('count'),
            func.sum(Invoice.amount).label('total_amount')
        ).group_by(
            Invoice.category
        ).all()
        
        distribution = []
        for category, count, total_amount in category_stats:
            distribution.append({
                'category': category.value,
                'category_label': category.value.replace('_', ' ').title(),
                'count': count,
                'total_amount': float(total_amount or 0)
            })
        
        return distribution
    
    def get_payment_method_distribution(self) -> List[Dict[str, Any]]:
        """
        Obtener distribución de facturas por método de pago.
        
        Returns:
            Lista de distribución por método de pago
        """
        payment_stats = self.db.query(
            Invoice.payment_method,
            func.count(Invoice.id).label('count'),
            func.sum(Invoice.amount).label('total_amount')
        ).group_by(
            Invoice.payment_method
        ).all()
        
        distribution = []
        for method, count, total_amount in payment_stats:
            distribution.append({
                'method': method.value,
                'method_label': method.value.replace('_', ' ').title(),
                'count': count,
                'total_amount': float(total_amount or 0)
            })
        
        return distribution
    
    def get_validation_performance(self) -> Dict[str, Any]:
        """
        Obtener métricas de rendimiento de validación.
        
        Returns:
            Dict con métricas de validación
        """
        # Obtener facturas validadas con fechas de validación
        validated_invoices = self.db.query(Invoice).filter(
            Invoice.status.in_([InvoiceStatus.VALIDATED, InvoiceStatus.REJECTED])
        ).all()
        
        if not validated_invoices:
            return {
                'avg_validation_time_hours': 0,
                'total_validated': 0,
                'validation_rate': 0
            }
        
        # Calcular tiempo promedio de validación (simulado)
        # En un sistema real, tendríamos timestamps de validación
        total_validated = len(validated_invoices)
        pending_count = self.db.query(Invoice).filter(
            Invoice.status == InvoiceStatus.PENDING
        ).count()
        
        total_invoices = total_validated + pending_count
        validation_rate = (total_validated / total_invoices * 100) if total_invoices > 0 else 0
        
        return {
            'avg_validation_time_hours': 24,  # Simulado
            'total_validated': total_validated,
            'validation_rate': round(validation_rate, 2)
        }
    
    def get_recent_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtener actividad reciente del sistema.
        
        Args:
            limit: Número máximo de actividades a retornar
            
        Returns:
            Lista de actividades recientes
        """
        recent_invoices = self.db.query(Invoice).join(
            User, Invoice.user_id == User.id
        ).order_by(
            Invoice.created_at.desc()
        ).limit(limit).all()
        
        activities = []
        for invoice in recent_invoices:
            activities.append({
                'id': invoice.id,
                'type': 'invoice_created',
                'description': f'Nueva factura de {invoice.provider} por ${invoice.amount:,.0f}',
                'user_name': invoice.user.name,
                'amount': float(invoice.amount),
                'status': invoice.status.value,
                'date': invoice.created_at.isoformat() if invoice.created_at else invoice.date.isoformat()
            })
        
        return activities


def get_dashboard_stats(db: Session) -> Dict[str, Any]:
    """
    Función principal para obtener todas las estadísticas del dashboard.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Dict con todas las estadísticas del dashboard
    """
    service = DashboardStatsService(db)
    
    return {
        'basic_stats': service.get_basic_stats(),
        'monthly_trends': service.get_monthly_trends(),
        'user_stats': service.get_user_stats(),
        'category_distribution': service.get_category_distribution(),
        'payment_method_distribution': service.get_payment_method_distribution(),
        'validation_performance': service.get_validation_performance(),
        'recent_activity': service.get_recent_activity()
    }
