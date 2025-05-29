"""Add settled_at column to trips

Revision ID: 1d510252c84a
Revises: 118a1aaa6c51
Create Date: 2025-05-26 18:17:44.558595

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d510252c84a'
down_revision: Union[str, None] = '118a1aaa6c51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

"""
    batch_alter_table() tells Alembic to use a copy-and-replace strategy, compatible with SQLite.
    Under the hood, Alembic creates a temporary table, copies your data, applies the changes, and swaps tables.
"""

def upgrade():
    with op.batch_alter_table("trips", schema=None) as batch_op:
        batch_op.add_column(sa.Column("settled_at", sa.DateTime(timezone=True), nullable=True))

def downgrade():
    with op.batch_alter_table("trips", schema=None) as batch_op:
        batch_op.drop_column("settled_at")


