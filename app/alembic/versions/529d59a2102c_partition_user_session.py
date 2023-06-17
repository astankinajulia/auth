"""partition user_session

Revision ID: 529d59a2102c
Revises: 2a211bd3252a
Create Date: 2023-06-17 15:37:08.323157

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '529d59a2102c'
down_revision = '2a211bd3252a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_session',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('user_id', sa.UUID(), nullable=True),
                    sa.Column('user_agent', sa.String(length=255), nullable=True),
                    sa.Column('auth_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
                    sa.Column('logout_date', sa.DateTime(timezone=True), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
                    sa.PrimaryKeyConstraint('id', 'auth_date'),
                    postgresql_partition_by='RANGE (auth_date)',
                    )
    op.execute("""CREATE TABLE IF NOT EXISTS "session_y2023m05" PARTITION OF "user_session" 
         FOR VALUES FROM ('2023-05-01') TO ('2023-06-01');""")
    op.execute("""CREATE TABLE IF NOT EXISTS "session_y2023m06" PARTITION OF "user_session" 
         FOR VALUES FROM ('2023-06-01') TO ('2023-07-01');""")
    op.execute(
        """CREATE TABLE IF NOT EXISTS "session_y2023m07" PARTITION OF "user_session" 
         FOR VALUES FROM ('2023-07-01') TO ('2023-08-01');"""
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_session')
    # ### end Alembic commands ###