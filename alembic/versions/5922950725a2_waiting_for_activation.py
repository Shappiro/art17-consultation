revision = '5922950725a2'
down_revision = '3c11e7800475'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('registered_users',
        sa.Column('waiting_for_activation',
            sa.Boolean(), server_default='0', nullable=False))


def downgrade():
    op.drop_column('registered_users', 'waiting_for_activation')
