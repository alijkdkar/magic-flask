"""empty message

Revision ID: 668950b52b04
Revises: 
Create Date: 2024-02-02 02:36:24.776625

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '668950b52b04'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('account',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('created', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated', sa.DateTime(timezone=True), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('dob', sa.Date(), nullable=True),
    sa.Column('country', sa.String(length=100), nullable=True),
    sa.Column('phone_number', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('account')
    # ### end Alembic commands ###