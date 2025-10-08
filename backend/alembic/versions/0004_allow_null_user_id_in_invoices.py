"""allow null user_id in invoices

Revision ID: 0004_allow_null_user_id
Revises: 0003_update_payment_methods_detailed
Create Date: 2025-10-05 16:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0004_allow_null_user_id'
down_revision = '0003_update_payment_methods_detailed'
branch_labels = None
depends_on = None


def upgrade():
    """Permitir que user_id sea null en la tabla invoices."""
    # Alterar la columna user_id para permitir valores null
    op.alter_column('invoices', 'user_id',
                    existing_type=sa.INTEGER(),
                    nullable=True)


def downgrade():
    """Revertir el cambio - hacer user_id obligatorio nuevamente."""
    # Primero eliminar facturas sin usuario (si las hay)
    op.execute("DELETE FROM invoices WHERE user_id IS NULL")
    
    # Luego hacer la columna obligatoria nuevamente
    op.alter_column('invoices', 'user_id',
                    existing_type=sa.INTEGER(),
                    nullable=False)
