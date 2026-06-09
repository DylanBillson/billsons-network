"""add selected location to users

Revision ID: 2b9a51013fd3
Revises: 23ffa1194d29
Create Date: 2026-06-09 14:34:05.078208
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2b9a51013fd3"
down_revision: Union[str, Sequence[str], None] = "23ffa1194d29"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "selected_location_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_index(
        op.f("ix_users_selected_location_id"),
        "users",
        ["selected_location_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_users_selected_location_id_locations",
        "users",
        "locations",
        ["selected_location_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_users_selected_location_id_locations",
        "users",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_users_selected_location_id"),
        table_name="users",
    )

    op.drop_column(
        "users",
        "selected_location_id",
    )