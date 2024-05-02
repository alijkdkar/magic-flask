"""add enName

Revision ID: e7a4c0c439f1
Revises: 40cbe4fad9d1
Create Date: 2024-05-03 00:45:01.994131

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e7a4c0c439f1'
down_revision = '40cbe4fad9d1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('category', schema=None) as batch_op:
        batch_op.add_column(sa.Column('enName', sa.String(length=100), nullable=True))

    with op.batch_alter_table('production_features', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('production_features', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    with op.batch_alter_table('category', schema=None) as batch_op:
        batch_op.drop_column('enName')

    # ### end Alembic commands ###
