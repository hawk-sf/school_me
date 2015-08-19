"""base api table

Revision ID: 5a82ea2e4d43
Revises: 2413d2c6e9b3
Create Date: 2015-08-11 16:13:43.963973

"""

# revision identifiers, used by Alembic.
revision = '5a82ea2e4d43'
down_revision = '2413d2c6e9b3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('base_apis',
    sa.Column('id', sa.Unicode(length=19), nullable=False),
    sa.Column('district_id', sa.Unicode(length=14), nullable=True),
    sa.Column('school_id', sa.Unicode(length=14), nullable=True),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('cds', sa.Unicode(length=14), nullable=True),
    sa.Column('rtype', sa.Unicode(length=1), nullable=True),
    sa.Column('stype', sa.Unicode(length=1), nullable=True),
    sa.Column('sped', sa.Unicode(length=1), nullable=True),
    sa.Column('size', sa.Unicode(length=1), nullable=True),
    sa.Column('flag', sa.Unicode(length=5), nullable=True),
    sa.Column('valid', sa.Integer(), nullable=True),
    sa.Column('api12b', sa.Integer(), nullable=True),
    sa.Column('st_rank', sa.Integer(), nullable=True),
    sa.Column('sim_rank', sa.Integer(), nullable=True),
    sa.Column('gr_targ', sa.Integer(), nullable=True),
    sa.Column('api_targ', sa.Integer(), nullable=True),
    sa.Column('aa_num', sa.Integer(), nullable=True),
    sa.Column('aa_sig', sa.Unicode(length=5), nullable=True),
    sa.Column('aa_api', sa.Integer(), nullable=True),
    sa.Column('aa_gt', sa.Integer(), nullable=True),
    sa.Column('aa_targ', sa.Integer(), nullable=True),
    sa.Column('ai_num', sa.Integer(), nullable=True),
    sa.Column('ai_sig', sa.Unicode(length=5), nullable=True),
    sa.Column('ai_api', sa.Integer(), nullable=True),
    sa.Column('ai_gt', sa.Integer(), nullable=True),
    sa.Column('ai_targ', sa.Integer(), nullable=True),
    sa.Column('as_num', sa.Integer(), nullable=True),
    sa.Column('as_sig', sa.Unicode(length=5), nullable=True),
    sa.Column('as_api', sa.Integer(), nullable=True),
    sa.Column('as_gt', sa.Integer(), nullable=True),
    sa.Column('as_targ', sa.Integer(), nullable=True),
    sa.Column('fi_num', sa.Integer(), nullable=True),
    sa.Column('fi_sig', sa.Unicode(length=5), nullable=True),
    sa.Column('fi_api', sa.Integer(), nullable=True),
    sa.Column('fi_gt', sa.Integer(), nullable=True),
    sa.Column('fi_targ', sa.Integer(), nullable=True),
    sa.Column('hi_num', sa.Integer(), nullable=True),
    sa.Column('hi_sig', sa.Unicode(length=5), nullable=True),
    sa.Column('hi_api', sa.Integer(), nullable=True),
    sa.Column('hi_gt', sa.Integer(), nullable=True),
    sa.Column('hi_targ', sa.Integer(), nullable=True),
    sa.Column('pi_num', sa.Integer(), nullable=True),
    sa.Column('pi_sig', sa.Unicode(length=5), nullable=True),
    sa.Column('pi_api', sa.Integer(), nullable=True),
    sa.Column('pi_gt', sa.Integer(), nullable=True),
    sa.Column('pi_targ', sa.Integer(), nullable=True),
    sa.Column('wh_num', sa.Integer(), nullable=True),
    sa.Column('wh_sig', sa.Unicode(length=5), nullable=True),
    sa.Column('wh_api', sa.Integer(), nullable=True),
    sa.Column('wh_gt', sa.Integer(), nullable=True),
    sa.Column('wh_targ', sa.Integer(), nullable=True),
    sa.Column('mr_num', sa.Integer(), nullable=True),
    sa.Column('mr_sig', sa.Unicode(length=5), nullable=True),
    sa.Column('mr_api', sa.Integer(), nullable=True),
    sa.Column('mr_gt', sa.Integer(), nullable=True),
    sa.Column('mr_targ', sa.Integer(), nullable=True),
    sa.Column('sd_num', sa.Integer(), nullable=True),
    sa.Column('sd_sig', sa.Unicode(length=5), nullable=True),
    sa.Column('sd_api', sa.Integer(), nullable=True),
    sa.Column('sd_gt', sa.Integer(), nullable=True),
    sa.Column('sd_targ', sa.Integer(), nullable=True),
    sa.Column('el_num', sa.Integer(), nullable=True),
    sa.Column('el_sig', sa.Unicode(length=5), nullable=True),
    sa.Column('el_api', sa.Integer(), nullable=True),
    sa.Column('el_gt', sa.Integer(), nullable=True),
    sa.Column('el_targ', sa.Integer(), nullable=True),
    sa.Column('di_num', sa.Integer(), nullable=True),
    sa.Column('di_sig', sa.Unicode(length=5), nullable=True),
    sa.Column('di_api', sa.Integer(), nullable=True),
    sa.Column('di_gt', sa.Integer(), nullable=True),
    sa.Column('di_targ', sa.Integer(), nullable=True),
    sa.Column('pct_aa', sa.Integer(), nullable=True),
    sa.Column('pct_ai', sa.Integer(), nullable=True),
    sa.Column('pct_as', sa.Integer(), nullable=True),
    sa.Column('pct_fi', sa.Integer(), nullable=True),
    sa.Column('pct_hi', sa.Integer(), nullable=True),
    sa.Column('pct_pi', sa.Integer(), nullable=True),
    sa.Column('pct_wh', sa.Integer(), nullable=True),
    sa.Column('pct_mr', sa.Integer(), nullable=True),
    sa.Column('meals', sa.Integer(), nullable=True),
    sa.Column('p_gate', sa.Integer(), nullable=True),
    sa.Column('p_miged', sa.Integer(), nullable=True),
    sa.Column('p_el', sa.Integer(), nullable=True),
    sa.Column('p_rfep', sa.Integer(), nullable=True),
    sa.Column('p_di', sa.Integer(), nullable=True),
    sa.Column('yr_rnd', sa.Unicode(length=5), nullable=True),
    sa.Column('cbmob', sa.Integer(), nullable=True),
    sa.Column('dmob', sa.Integer(), nullable=True),
    sa.Column('acs_k3', sa.Integer(), nullable=True),
    sa.Column('acs_46', sa.Integer(), nullable=True),
    sa.Column('acs_core', sa.Integer(), nullable=True),
    sa.Column('pct_resp', sa.Integer(), nullable=True),
    sa.Column('not_hsg', sa.Integer(), nullable=True),
    sa.Column('hsg', sa.Integer(), nullable=True),
    sa.Column('some_col', sa.Integer(), nullable=True),
    sa.Column('col_grad', sa.Integer(), nullable=True),
    sa.Column('grad_sch', sa.Integer(), nullable=True),
    sa.Column('avg_ed', sa.Float(), nullable=True),
    sa.Column('full', sa.Integer(), nullable=True),
    sa.Column('emer', sa.Integer(), nullable=True),
    sa.Column('pen_2', sa.Integer(), nullable=True),
    sa.Column('pen_35', sa.Integer(), nullable=True),
    sa.Column('pen_6', sa.Integer(), nullable=True),
    sa.Column('pen_78', sa.Integer(), nullable=True),
    sa.Column('pen_91', sa.Integer(), nullable=True),
    sa.Column('enroll', sa.Integer(), nullable=True),
    sa.Column('parent_opt', sa.Integer(), nullable=True),
    sa.Column('tested', sa.Integer(), nullable=True),
    sa.Column('sci', sa.Float(), nullable=True),
    sa.Column('vcst_e28', sa.Integer(), nullable=True),
    sa.Column('pcst_e28', sa.Float(), nullable=True),
    sa.Column('vcst_e91', sa.Integer(), nullable=True),
    sa.Column('pcst_e91', sa.Float(), nullable=True),
    sa.Column('cw_cste', sa.Float(), nullable=True),
    sa.Column('vcst_m28', sa.Integer(), nullable=True),
    sa.Column('pcst_m28', sa.Float(), nullable=True),
    sa.Column('vcst_m91', sa.Integer(), nullable=True),
    sa.Column('pcst_m91', sa.Float(), nullable=True),
    sa.Column('cw_cstm', sa.Float(), nullable=True),
    sa.Column('vcst_s28', sa.Integer(), nullable=True),
    sa.Column('pcst_s28', sa.Float(), nullable=True),
    sa.Column('vcst_s91', sa.Integer(), nullable=True),
    sa.Column('pcst_s91', sa.Float(), nullable=True),
    sa.Column('cws_91', sa.Float(), nullable=True),
    sa.Column('vcst_h28', sa.Integer(), nullable=True),
    sa.Column('pcst_h28', sa.Float(), nullable=True),
    sa.Column('vcst_h91', sa.Integer(), nullable=True),
    sa.Column('pcst_h91', sa.Float(), nullable=True),
    sa.Column('cw_csth', sa.Float(), nullable=True),
    sa.Column('vchs_e91', sa.Float(), nullable=True),
    sa.Column('pchs_e91', sa.Float(), nullable=True),
    sa.Column('cw_chse', sa.Float(), nullable=True),
    sa.Column('vchs_m91', sa.Float(), nullable=True),
    sa.Column('pchs_m91', sa.Float(), nullable=True),
    sa.Column('cw_chsm', sa.Float(), nullable=True),
    sa.Column('tot_28', sa.Float(), nullable=True),
    sa.Column('tot_91', sa.Float(), nullable=True),
    sa.Column('cw_sci', sa.Float(), nullable=True),
    sa.Column('vcst_ls10', sa.Integer(), nullable=True),
    sa.Column('pcst_ls10', sa.Float(), nullable=True),
    sa.Column('cwm2_28', sa.Float(), nullable=True),
    sa.Column('vcstm2_28', sa.Integer(), nullable=True),
    sa.Column('pcstm2_28', sa.Float(), nullable=True),
    sa.Column('cwm2_91', sa.Float(), nullable=True),
    sa.Column('vcstm2_91', sa.Integer(), nullable=True),
    sa.Column('pcstm2_91', sa.Float(), nullable=True),
    sa.Column('cws2_91', sa.Float(), nullable=True),
    sa.Column('vcsts2_91', sa.Integer(), nullable=True),
    sa.Column('pcsts2_91', sa.Float(), nullable=True),
    sa.Column('irg5', sa.Unicode(length=1), nullable=True),
    sa.ForeignKeyConstraint(['district_id'], [u'districts.cds_code'], ),
    sa.ForeignKeyConstraint(['school_id'], [u'schools.cds_code'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column(u'schools', 'charter',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(u'schools', 'charter',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.drop_table('base_apis')
    ### end Alembic commands ###
