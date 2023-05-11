"""add logout_date to session

Revision ID: e925727685f9
Revises: 93edddfbad48
Create Date: 2023-05-10 01:03:12.887859

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision = 'e925727685f9'
down_revision = '93edddfbad48'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'session',
        sa.Column(
            'logout_date',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=True,
        )
    )


def downgrade() -> None:
    op.drop_column('session','logout_date')

