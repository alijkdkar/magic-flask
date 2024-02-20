"""empty message

Revision ID: 98e897083f08
Revises: 392855e8905e
Create Date: 2024-02-20 23:05:39.827710

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '98e897083f08'
down_revision = '392855e8905e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    culture = postgresql.ENUM('fa', 'en', 'fe', name='Culture')
    culture.create(op.get_bind(), checkfirst=True)
    role = postgresql.ENUM('admin', 'semiAdmin', 'manager', 'blogger', 'simple', 'guest', name='Role')
    role.create(op.get_bind(), checkfirst=True)
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.add_column(sa.Column('culture', culture, nullable=True))
        batch_op.add_column(sa.Column('role',role , nullable=True))
        

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.drop_column('role')
        batch_op.drop_column('culture')

    # ### end Alembic commands ###
