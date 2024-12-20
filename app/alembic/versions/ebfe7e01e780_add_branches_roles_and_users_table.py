"""add branches roles and users table

Revision ID: ebfe7e01e780
Revises: dda5698b3b4f
Create Date: 2024-11-08 10:53:57.310532

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ebfe7e01e780'
down_revision: Union[str, None] = 'dda5698b3b4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'branches',
        sa.Column('branch_id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(), unique=True, index=True),
        sa.Column('address', sa.String(), nullable=False),
        sa.Column('phone_number', sa.String(), nullable=False, unique=True),
        sa.Column('branch_manager', sa.String(), nullable=False),
    )

    op.create_table(
        'roles',
        sa.Column('role_id', sa.Integer(), primary_key=True, index=True),
        sa.Column('role_name', sa.String(), unique=True),
    )

    op.create_table(
        'users',
        sa.Column('user_id', sa.Integer(), primary_key=True, index=True),
        sa.Column('first_name', sa.String()),
        sa.Column('last_name', sa.String()),
        sa.Column('email', sa.String(), unique=True, index=True),
        sa.Column('hashed_password', sa.String()),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.role_id')),
        sa.Column('branch_id', sa.Integer(), sa.ForeignKey('branches.branch_id'), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.drop_table('roles')
    op.drop_table('branches')
    # ### end Alembic commands ###