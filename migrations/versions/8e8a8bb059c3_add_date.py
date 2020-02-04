"""add date

Revision ID: 8e8a8bb059c3
Revises: ab66c6dd082b
Create Date: 2020-02-04 13:14:08.020559

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e8a8bb059c3'
down_revision = 'ab66c6dd082b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('poem', sa.Column('date', sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('poem', 'date')
    # ### end Alembic commands ###
