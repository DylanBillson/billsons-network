"""make device name unique for active devices only

Revision ID: 88c6505e6a71
Revises: 2b9a51013fd3
Create Date: 2026-06-18 11:06:14.684023
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "88c6505e6a71"
down_revision: Union[str, Sequence[str], None] = "2b9a51013fd3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index(
        "ix_devices_name",
        table_name="devices",
    )

    op.create_index(
        "uq_devices_name_active",
        "devices",
        ["name"],
        unique=True,
        postgresql_where=sa.text("is_deleted = false"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_devices_name_active",
        table_name="devices",
    )

    op.create_index(
        "ix_devices_name",
        "devices",
        ["name"],
        unique=True,
    )