"""update_payment_methods_detailed

Revision ID: 0003
Revises: 0002_add_nit_field_to_invoices
Create Date: 2025-10-02 08:36:11.087843

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002_add_nit_field_to_invoices'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Actualizar el enum PaymentMethod para incluir opciones detalladas.
    """
    # Crear el nuevo enum con las opciones detalladas
    op.execute("CREATE TYPE paymentmethod_new AS ENUM ('efectivo', 'tarjeta_bst', 'tarjeta_personal', 'transferencia')")
    
    # Actualizar la columna para usar el nuevo enum
    op.execute("ALTER TABLE invoices ALTER COLUMN payment_method TYPE paymentmethod_new USING payment_method::text::paymentmethod_new")
    
    # Eliminar el enum antiguo
    op.execute("DROP TYPE paymentmethod")
    
    # Renombrar el nuevo enum
    op.execute("ALTER TYPE paymentmethod_new RENAME TO paymentmethod")


def downgrade() -> None:
    """
    Revertir a los métodos de pago originales.
    """
    # Crear el enum original
    op.execute("CREATE TYPE paymentmethod_old AS ENUM ('efectivo', 'tarjeta', 'transferencia')")
    
    # Actualizar la columna para usar el enum original
    # Mapear los nuevos valores a los originales
    op.execute("""
        ALTER TABLE invoices ALTER COLUMN payment_method TYPE paymentmethod_old 
        USING CASE 
            WHEN payment_method::text = 'tarjeta_bst' THEN 'tarjeta'::paymentmethod_old
            WHEN payment_method::text = 'tarjeta_personal' THEN 'tarjeta'::paymentmethod_old
            ELSE payment_method::text::paymentmethod_old
        END
    """)
    
    # Eliminar el enum nuevo
    op.execute("DROP TYPE paymentmethod")
    
    # Renombrar el enum original
    op.execute("ALTER TYPE paymentmethod_old RENAME TO paymentmethod")
