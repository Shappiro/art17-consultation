revision = '49408eeb4094'
down_revision = 'b9277e0bbc9'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column('lu_habitattypes_manual_assessments_2007', sa.Column('backcasted_2007', sa.String(length=4), nullable=True))
    op.add_column('lu_habitattypes_manual_assessments_2007', sa.Column('conclusion_assessment_prev', sa.String(length=3), nullable=True))
    op.add_column('lu_habitattypes_manual_assessments_2007', sa.Column('conclusion_assessment_trend_prev', sa.String(length=20), nullable=True))

def downgrade():
    op.drop_column('lu_habitattypes_manual_assessments_2007', 'conclusion_assessment_trend_prev')
    op.drop_column('lu_habitattypes_manual_assessments_2007', 'conclusion_assessment_prev')
    op.drop_column('lu_habitattypes_manual_assessments_2007', 'backcasted_2007')
