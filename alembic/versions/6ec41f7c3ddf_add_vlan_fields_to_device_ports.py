"""add vlan fields to device ports

Revision ID: 6ec41f7c3ddf
Revises: 88c6505e6a71
Create Date: 2026-06-18 15:12:58.738126
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "6ec41f7c3ddf"
down_revision: Union[str, Sequence[str], None] = "88c6505e6a71"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "device_ports",
        sa.Column("vlan_id", sa.Integer(), nullable=True),
    )

    op.add_column(
        "device_ports",
        sa.Column(
            "vlan_mode",
            sa.String(length=50),
            nullable=False,
            server_default="none",
        ),
    )

    op.add_column(
        "device_ports",
        sa.Column("vlan_notes", sa.Text(), nullable=True),
    )

    op.create_index(
        op.f("ix_device_ports_vlan_id"),
        "device_ports",
        ["vlan_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_device_ports_vlan_id_vlans",
        "device_ports",
        "vlans",
        ["vlan_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.alter_column(
        "device_ports",
        "vlan_mode",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_device_ports_vlan_id_vlans",
        "device_ports",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_device_ports_vlan_id"),
        table_name="device_ports",
    )

    op.drop_column("device_ports", "vlan_notes")
    op.drop_column("device_ports", "vlan_mode")
    op.drop_column("device_ports", "vlan_id")