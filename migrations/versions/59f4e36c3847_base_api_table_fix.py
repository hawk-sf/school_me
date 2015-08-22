"""base api table fix

Revision ID: 59f4e36c3847
Revises: 5a82ea2e4d43
Create Date: 2015-08-11 16:23:44.549574

"""

# revision identifiers, used by Alembic.
revision = '59f4e36c3847'
down_revision = '5a82ea2e4d43'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('base_apis', sa.Column('apib', sa.Integer(), nullable=True))
    op.drop_column('base_apis', 'api12b')
    op.alter_column('schools', 'charter',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('schools', 'charter',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.add_column('base_apis', sa.Column('api12b', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_column('base_apis', 'apib')
    ### end Alembic commands ###