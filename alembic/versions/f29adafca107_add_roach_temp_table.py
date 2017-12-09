"""add_roach_temp_table

Revision ID: f29adafca107
Revises: 38aa03a7c923
Create Date: 2017-12-09 19:59:50.058296+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f29adafca107'
down_revision = '64bc793c6237'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roach_temperature',
    sa.Column('time', sa.BigInteger(), nullable=False),
    sa.Column('roach', sa.Integer(), nullable=False),
    sa.Column('ambient_temp', sa.Float(), nullable=True),
    sa.Column('inlet_temp', sa.Float(), nullable=True),
    sa.Column('outlet_temp', sa.Float(), nullable=True),
    sa.Column('fpga_temp', sa.Float(), nullable=True),
    sa.Column('ppc_temp', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('time', 'roach')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('roach_temperature')
    # ### end Alembic commands ###
