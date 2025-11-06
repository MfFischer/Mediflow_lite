"""add_user_fields_full_name_prc_license

Revision ID: 75281a63a045
Revises: 9d6f1910b78c
Create Date: 2025-11-06 22:00:40.084158

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '75281a63a045'
down_revision = '9d6f1910b78c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add full_name column
    op.add_column('users', sa.Column('full_name', sa.String(), nullable=True))

    # Add prc_license column for doctors
    op.add_column('users', sa.Column('prc_license', sa.String(), nullable=True))

    # Make email nullable (for existing users)
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('email', nullable=True)


def downgrade() -> None:
    # Remove added columns
    op.drop_column('users', 'prc_license')
    op.drop_column('users', 'full_name')

    # Revert email to non-nullable
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('email', nullable=False)

