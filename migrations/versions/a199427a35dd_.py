"""empty message

Revision ID: a199427a35dd
Revises: 
Create Date: 2020-05-25 18:50:47.736357

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a199427a35dd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('image_id', sa.String(length=256), nullable=True))
    op.add_column('posts', sa.Column('image_url', sa.String(length=256), nullable=True))
    op.add_column('users', sa.Column('image_id', sa.String(length=256), nullable=True))
    op.add_column('users', sa.Column('image_url', sa.String(length=256), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'image_url')
    op.drop_column('users', 'image_id')
    op.drop_column('posts', 'image_url')
    op.drop_column('posts', 'image_id')
    # ### end Alembic commands ###
