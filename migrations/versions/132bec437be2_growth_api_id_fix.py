"""growth api id fix

Revision ID: 132bec437be2
Revises: 9c52668cef8
Create Date: 2015-08-10 23:31:31.942729

"""

# revision identifiers, used by Alembic.
revision = '132bec437be2'
down_revision = '9c52668cef8'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('growth_apis', 'id',
               existing_type=mysql.VARCHAR(length=18),
               type_=sa.Unicode(length=19),
               existing_nullable=False)
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
    op.alter_column('growth_apis', 'id',
               existing_type=sa.Unicode(length=19),
               type_=mysql.VARCHAR(length=18),
               existing_nullable=False)
    ### end Alembic commands ###