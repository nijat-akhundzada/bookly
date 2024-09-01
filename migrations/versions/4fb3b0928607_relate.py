"""relate

Revision ID: 4fb3b0928607
Revises: cfcf7c02be90
Create Date: 2024-08-29 10:16:53.976121

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '4fb3b0928607'
down_revision: Union[str, None] = 'cfcf7c02be90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('books', sa.Column('user_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(None, 'books', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'books', type_='foreignkey')
    op.drop_column('books', 'user_id')
    # ### end Alembic commands ###