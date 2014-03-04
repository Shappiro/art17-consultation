revision = '130a02d9729f'
down_revision = '3e53b8bd1162'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('config',
        sa.Column('habitat_map_url', sa.String(length=255), nullable=True),
    )
    op.add_column('config',
        sa.Column('species_map_url', sa.String(length=255), nullable=True),
    )

    op.execute("UPDATE config SET habitat_map_url='', species_map_url=''")


def downgrade():
    op.drop_column('config', 'species_map_url')
    op.drop_column('config', 'habitat_map_url')
