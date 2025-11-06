"""add_philippine_insurance_and_hospital_settings

Revision ID: 9d6f1910b78c
Revises: 8d555c9f8910
Create Date: 2025-11-06 20:57:10.763635

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d6f1910b78c'
down_revision = '8d555c9f8910'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add Philippine insurance fields to patients table
    op.add_column('patients', sa.Column('philhealth_number', sa.String(20), nullable=True))
    op.add_column('patients', sa.Column('philhealth_member_type', sa.String(50), nullable=True))
    op.add_column('patients', sa.Column('hmo_provider', sa.String(100), nullable=True))
    op.add_column('patients', sa.Column('hmo_card_number', sa.String(100), nullable=True))
    op.add_column('patients', sa.Column('hmo_coverage_limit', sa.String(50), nullable=True))
    op.add_column('patients', sa.Column('hmo_validity_date', sa.Date(), nullable=True))

    # Add insurance coverage fields to invoices table
    op.add_column('invoices', sa.Column('philhealth_coverage', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('invoices', sa.Column('hmo_coverage', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('invoices', sa.Column('senior_pwd_discount', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('invoices', sa.Column('patient_balance', sa.Float(), nullable=False, server_default='0.0'))

    # Add category and doctor fields to invoice_items table
    op.add_column('invoice_items', sa.Column('category', sa.String(50), nullable=False, server_default='other'))
    op.add_column('invoice_items', sa.Column('doctor_name', sa.String(200), nullable=True))
    op.add_column('invoice_items', sa.Column('doctor_license', sa.String(50), nullable=True))

    # Create hospital_settings table
    op.create_table(
        'hospital_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hospital_name', sa.String(200), nullable=False, server_default='Medical Center'),
        sa.Column('hospital_address', sa.Text(), nullable=True),
        sa.Column('hospital_phone', sa.String(50), nullable=True),
        sa.Column('hospital_email', sa.String(100), nullable=True),
        sa.Column('hospital_website', sa.String(200), nullable=True),
        sa.Column('doh_license_number', sa.String(100), nullable=True),
        sa.Column('tin', sa.String(50), nullable=True),
        sa.Column('philhealth_accreditation', sa.String(100), nullable=True),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('invoice_prefix', sa.String(10), nullable=False, server_default='INV'),
        sa.Column('invoice_footer', sa.Text(), nullable=True),
        sa.Column('authorized_signatory', sa.String(200), nullable=True),
        sa.Column('signatory_title', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Insert default hospital settings
    op.execute("""
        INSERT INTO hospital_settings (hospital_name, invoice_prefix, created_at, updated_at)
        VALUES ('Medical Center', 'INV', datetime('now'), datetime('now'))
    """)


def downgrade() -> None:
    # Drop hospital_settings table
    op.drop_table('hospital_settings')

    # Remove fields from invoice_items
    op.drop_column('invoice_items', 'doctor_license')
    op.drop_column('invoice_items', 'doctor_name')
    op.drop_column('invoice_items', 'category')

    # Remove insurance fields from invoices
    op.drop_column('invoices', 'patient_balance')
    op.drop_column('invoices', 'senior_pwd_discount')
    op.drop_column('invoices', 'hmo_coverage')
    op.drop_column('invoices', 'philhealth_coverage')

    # Remove Philippine insurance fields from patients
    op.drop_column('patients', 'hmo_validity_date')
    op.drop_column('patients', 'hmo_coverage_limit')
    op.drop_column('patients', 'hmo_card_number')
    op.drop_column('patients', 'hmo_provider')
    op.drop_column('patients', 'philhealth_member_type')
    op.drop_column('patients', 'philhealth_number')

