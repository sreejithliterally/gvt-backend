"""Add Attendance and LeaveApplication tables

Revision ID: 20cab865278b
Revises: ebfe7e01e780
Create Date: 2024-11-08 11:13:08.249201

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20cab865278b'
down_revision: Union[str, None] = 'ebfe7e01e780'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create Attendance table
    op.create_table(
        'attendance',
        sa.Column('attendance_id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),  # e.g., 'present', 'absent', 'leave'
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
    )
    op.create_index(op.f('ix_attendance_user_id'), 'attendance', ['user_id'])
    op.create_index(op.f('ix_attendance_date'), 'attendance', ['date'])

    # Create LeaveApplication table
    op.create_table(
        'leave_applications',
        sa.Column('leave_id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('leave_date', sa.Date(), nullable=False),
        sa.Column('reason', sa.String(), nullable=True),
        sa.Column('status', sa.String(), default='pending'),  # e.g., 'pending', 'approved', 'rejected'
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
    )
    op.create_index(op.f('ix_leave_applications_user_id'), 'leave_applications', ['user_id'])
    op.create_index(op.f('ix_leave_applications_leave_date'), 'leave_applications', ['leave_date'])


def downgrade():
    # Drop LeaveApplication table
    op.drop_index(op.f('ix_leave_applications_leave_date'), table_name='leave_applications')
    op.drop_index(op.f('ix_leave_applications_user_id'), table_name='leave_applications')
    op.drop_table('leave_applications')

    # Drop Attendance table
    op.drop_index(op.f('ix_attendance_date'), table_name='attendance')
    op.drop_index(op.f('ix_attendance_user_id'), table_name='attendance')
    op.drop_table('attendance')