revision = 'b9277e0bbc9'
down_revision = '30882fca6e39'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():

    op.alter_column('etc_data_habitattype_regions', 'filename',
                  existing_type=sa.String(length=60), type_=sa.String(length=300)),

    op.alter_column('etc_dic_method', 'method',
                  existing_type=sa.String(length=3), type_=sa.String(length=10)),

    op.alter_column('etc_data_habitattype_automatic_assessment', 'assessment_method',
                  existing_type=sa.String(length=3), type_=sa.String(length=10)),

    op.alter_column('etc_data_habitattype_automatic_assessment', 'country',
                  existing_type=sa.String(length=3), type_=sa.String(length=4)),

def downgrade():

    op.alter_column('etc_data_habitattype_automatic_assessment', 'country',
                  existing_type=sa.String(length=4), type_=sa.String(length=3)),

    op.alter_column('etc_data_habitattype_automatic_assessment', 'assessment_method',
                  existing_type=sa.String(length=10), type_=sa.String(length=3)),

    op.alter_column('etc_dic_method', 'method',
                  existing_type=sa.String(length=10), type_=sa.String(length=3)),

    op.alter_column('etc_data_habitattype_regions', 'filename',
                  existing_type=sa.String(length=300), type_=sa.String(length=60)),