
revision = '2de9ca3db59d'
down_revision = '4c5f00269981'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.oracle import NVARCHAR2
from sqlalchemy.sql import table, column

period_tables = [
    'dic_country_codes',
    'etc_data_habitattype_automatic_assessment',
    'etc_data_habitattype_regions',
    'etc_data_hcoverage_pressures',
    'etc_data_hcoverage_threats',
    'etc_data_species_automatic_assessment',
    'etc_data_species_regions',
    'etc_data_spopulation_pressures',
    'etc_data_spopulation_threats',
    'etc_dic_biogeoreg',
    'etc_dic_conclusion',
    'etc_dic_decision',
    'etc_dic_hd_habitats',
    'etc_dic_method',
    'etc_dic_population_units',
    'etc_dic_species_type',
    'etc_dic_trend',
    'etc_qa_errors_habitattype_manual_checked',
    'etc_qa_errors_species_manual_checked',
    'habitat_comments',
    #'habitat_group',
    #'species_group',
    'habitats2eunis',
    'habitattypes_manual_assessment',
    'lu_hd_habitats',
    'photo_habitats',
    'photo_species',
    'restricted_habitats',
    'restricted_species',
    #'species_name',
    'species_manual_assessment',
    'wiki',
    'wiki_trail',
]


def upgrade():
    op.create_table('datasets',
                    sa.Column('id', sa.Integer, nullable=False),
                    sa.Column('name', NVARCHAR2(255), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
    )
    datasets_table = table(
        'datasets',
        column('id', sa.Integer),
        column('name', sa.String),
    )
    op.bulk_insert(datasets_table,
                   [
                       {'id': 1, 'name': '2001-2006'},
                       {'id': 2, 'name': '2007-2012'},
                   ]
    )
    for tbl in period_tables:
        op.add_column(tbl,
                      sa.Column('ext_dataset_id', sa.Integer, nullable=True),
        )
        op.execute("UPDATE `%s` SET `ext_dataset_id`='1'" % tbl)


def downgrade():
    for tbl in period_tables:
        op.drop_column(tbl, 'ext_dataset_id')
    op.drop_table('datasets')
