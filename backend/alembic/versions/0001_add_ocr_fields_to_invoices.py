"""Add OCR fields to invoices

Revision ID: 0001
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add OCR fields to invoices table."""
    # Add OCR fields to invoices table
    op.add_column('invoices', sa.Column('ocr_data', sa.JSON(), nullable=True))
    op.add_column('invoices', sa.Column('ocr_confidence', sa.Float(), nullable=True))


def downgrade():
    """Remove OCR fields from invoices table."""
    op.drop_column('invoices', 'ocr_confidence')
    op.drop_column('invoices', 'ocr_data')
