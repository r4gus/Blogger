"""filename

Revision ID: 9fcb1c5dbce6
Revises: fd7b0c1c9432
Create Date: 2020-04-06 17:44:43.839027

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9fcb1c5dbce6'
down_revision = 'fd7b0c1c9432'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('image_name', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'image_name')
    # ### end Alembic commands ###
