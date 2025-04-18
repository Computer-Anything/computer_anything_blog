"""Add upvotes and downvotes to blog_posts

Revision ID: cc13bdacb968
Revises: 187ec2bd9b1b
Create Date: 2025-04-15 10:08:52.359027

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc13bdacb968'
down_revision = '187ec2bd9b1b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('blog_posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('upvotes', sa.Integer(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('downvotes', sa.Integer(), nullable=False, server_default='0'))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('blog_posts', schema=None) as batch_op:
        batch_op.drop_column('downvotes')
        batch_op.drop_column('upvotes')

    # ### end Alembic commands ###
