"""descriptions

Revision ID: 8bf3428c3612
Revises: 15f913cb40db
Create Date: 2020-11-16 15:10:49.779287

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8bf3428c3612'
down_revision = '15f913cb40db'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('collection', sa.Column('description', sa.String(length=256), nullable=True))
    op.add_column('piece', sa.Column('description', sa.String(length=256), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('piece', 'description')
    op.drop_column('collection', 'description')
    # ### end Alembic commands ###
