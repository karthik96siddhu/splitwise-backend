"""modify trip_members table

Revision ID: 118a1aaa6c51
Revises: 658f2de22621
Create Date: 2025-05-10 20:15:40.639168

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '118a1aaa6c51'
down_revision: Union[str, None] = '658f2de22621'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema using batch mode for SQLite compatibility."""
    with op.batch_alter_table("trip_members", recreate="always") as batch_op:
        batch_op.create_foreign_key(
            "fk_trip_members_trip_id",
            "trips",
            ["trip_id"],
            ["id"],
            ondelete="CASCADE"
        )
        batch_op.create_foreign_key(
            "fk_trip_members_user_id",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE"
        )

def downgrade() -> None:
    """Downgrade schema using batch mode for SQLite compatibility."""
    with op.batch_alter_table("trip_members", recreate="always") as batch_op:
        batch_op.create_foreign_key(
            "fk_trip_members_trip_id",
            "trips",
            ["trip_id"],
            ["id"]
        )
        batch_op.create_foreign_key(
            "fk_trip_members_user_id",
            "users",
            ["user_id"],
            ["id"]
        )

