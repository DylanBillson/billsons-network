"""initial schema

Revision ID: 23ffa1194d29
Revises:
Create Date: 2026-06-09 09:39:55.477208
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "23ffa1194d29"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("username_snapshot", sa.String(length=100), nullable=True),
        sa.Column("action", sa.String(length=150), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=True),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(length=100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_logs_action"), "audit_logs", ["action"])
    op.create_index(op.f("ix_audit_logs_created_at"), "audit_logs", ["created_at"])
    op.create_index(op.f("ix_audit_logs_entity_id"), "audit_logs", ["entity_id"])
    op.create_index(op.f("ix_audit_logs_entity_type"), "audit_logs", ["entity_type"])
    op.create_index(op.f("ix_audit_logs_id"), "audit_logs", ["id"])
    op.create_index(op.f("ix_audit_logs_user_id"), "audit_logs", ["user_id"])

    op.create_table(
        "device_types",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("slug", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon_path", sa.Text(), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_device_types_id"), "device_types", ["id"])
    op.create_index(op.f("ix_device_types_name"), "device_types", ["name"], unique=True)
    op.create_index(op.f("ix_device_types_slug"), "device_types", ["slug"], unique=True)

    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("parent_location_id", sa.Integer(), nullable=True),
        sa.Column("upstream_device_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["parent_location_id"],
            ["locations.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_locations_id"), "locations", ["id"])
    op.create_index(op.f("ix_locations_name"), "locations", ["name"], unique=True)
    op.create_index(
        op.f("ix_locations_parent_location_id"),
        "locations",
        ["parent_location_id"],
    )
    op.create_index(
        op.f("ix_locations_upstream_device_id"),
        "locations",
        ["upstream_device_id"],
    )

    op.create_table(
        "settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("setting_key", sa.String(length=150), nullable=False),
        sa.Column("setting_value", sa.Text(), nullable=True),
        sa.Column("value_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_settings_id"), "settings", ["id"])
    op.create_index(
        op.f("ix_settings_setting_key"),
        "settings",
        ["setting_key"],
        unique=True,
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"])
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.create_table(
        "admin_notes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_admin_notes_created_by"), "admin_notes", ["created_by"])
    op.create_index(op.f("ix_admin_notes_id"), "admin_notes", ["id"])
    op.create_index(op.f("ix_admin_notes_location_id"), "admin_notes", ["location_id"])
    op.create_index(op.f("ix_admin_notes_updated_by"), "admin_notes", ["updated_by"])

    op.create_table(
        "vlans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("vlan_number", sa.Integer(), nullable=False),
        sa.Column("purpose", sa.Text(), nullable=True),
        sa.Column("subnet", sa.String(length=100), nullable=True),
        sa.Column("gateway", sa.String(length=100), nullable=True),
        sa.Column("dhcp_range_start", sa.String(length=100), nullable=True),
        sa.Column("dhcp_range_end", sa.String(length=100), nullable=True),
        sa.Column("dns_settings", sa.Text(), nullable=True),
        sa.Column("firewall_notes", sa.Text(), nullable=True),
        sa.Column("allowed_access_rules", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("location_id", "name", name="uq_vlans_location_id_name"),
        sa.UniqueConstraint(
            "location_id",
            "vlan_number",
            name="uq_vlans_location_id_vlan_number",
        ),
    )
    op.create_index(op.f("ix_vlans_id"), "vlans", ["id"])
    op.create_index(op.f("ix_vlans_location_id"), "vlans", ["location_id"])

    op.create_table(
        "devices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("device_type_id", sa.Integer(), nullable=False),
        sa.Column("manufacturer", sa.String(length=255), nullable=True),
        sa.Column("model", sa.String(length=255), nullable=True),
        sa.Column("serial_number", sa.String(length=255), nullable=True),
        sa.Column("mac_address", sa.String(length=100), nullable=True),
        sa.Column("ip_assignment_type", sa.String(length=50), nullable=True),
        sa.Column("ip_address", sa.String(length=100), nullable=True),
        sa.Column("vlan_id", sa.Integer(), nullable=True),
        sa.Column("power_source", sa.String(length=50), nullable=False),
        sa.Column("supplied_by", sa.String(length=255), nullable=True),
        sa.Column("purchase_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("photo_path", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["device_type_id"],
            ["device_types.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["vlan_id"], ["vlans.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_devices_device_type_id"), "devices", ["device_type_id"])
    op.create_index(op.f("ix_devices_id"), "devices", ["id"])
    op.create_index(op.f("ix_devices_ip_address"), "devices", ["ip_address"])
    op.create_index(op.f("ix_devices_location_id"), "devices", ["location_id"])
    op.create_index(op.f("ix_devices_name"), "devices", ["name"], unique=True)
    op.create_index(op.f("ix_devices_status"), "devices", ["status"])
    op.create_index(op.f("ix_devices_vlan_id"), "devices", ["vlan_id"])

    op.create_table(
        "ssids",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("encrypted_password", sa.Text(), nullable=True),
        sa.Column("security_type", sa.String(length=100), nullable=True),
        sa.Column("vlan_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["vlan_id"], ["vlans.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("location_id", "name", name="uq_ssids_location_id_name"),
    )
    op.create_index(op.f("ix_ssids_id"), "ssids", ["id"])
    op.create_index(op.f("ix_ssids_location_id"), "ssids", ["location_id"])
    op.create_index(op.f("ix_ssids_vlan_id"), "ssids", ["vlan_id"])

    op.create_table(
        "device_ports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=100), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "device_id",
            "label",
            name="uq_device_ports_device_id_label",
        ),
        sa.UniqueConstraint(
            "device_id",
            "sort_order",
            name="uq_device_ports_device_id_sort_order",
        ),
    )
    op.create_index(op.f("ix_device_ports_device_id"), "device_ports", ["device_id"])
    op.create_index(op.f("ix_device_ports_id"), "device_ports", ["id"])

    op.create_table(
        "port_forwarding_rules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("router_device_id", sa.Integer(), nullable=False),
        sa.Column("rule_name", sa.String(length=255), nullable=False),
        sa.Column("external_port_start", sa.Integer(), nullable=False),
        sa.Column("external_port_end", sa.Integer(), nullable=True),
        sa.Column("internal_ip_address", sa.String(length=100), nullable=False),
        sa.Column("internal_port_start", sa.Integer(), nullable=False),
        sa.Column("internal_port_end", sa.Integer(), nullable=True),
        sa.Column("protocol", sa.String(length=50), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.Integer(), nullable=True),
        sa.CheckConstraint(
            "external_port_end IS NULL OR external_port_end >= external_port_start",
            name="ck_port_forwarding_external_port_order",
        ),
        sa.CheckConstraint(
            "external_port_end IS NULL OR external_port_end BETWEEN 1 AND 65535",
            name="ck_port_forwarding_external_port_end_range",
        ),
        sa.CheckConstraint(
            "external_port_start BETWEEN 1 AND 65535",
            name="ck_port_forwarding_external_port_start_range",
        ),
        sa.CheckConstraint(
            "internal_port_end IS NULL OR internal_port_end >= internal_port_start",
            name="ck_port_forwarding_internal_port_order",
        ),
        sa.CheckConstraint(
            "internal_port_end IS NULL OR internal_port_end BETWEEN 1 AND 65535",
            name="ck_port_forwarding_internal_port_end_range",
        ),
        sa.CheckConstraint(
            "internal_port_start BETWEEN 1 AND 65535",
            name="ck_port_forwarding_internal_port_start_range",
        ),
        sa.ForeignKeyConstraint(
            ["router_device_id"],
            ["devices.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_port_forwarding_rules_id"),
        "port_forwarding_rules",
        ["id"],
    )
    op.create_index(
        op.f("ix_port_forwarding_rules_internal_ip_address"),
        "port_forwarding_rules",
        ["internal_ip_address"],
    )
    op.create_index(
        op.f("ix_port_forwarding_rules_is_enabled"),
        "port_forwarding_rules",
        ["is_enabled"],
    )
    op.create_index(
        op.f("ix_port_forwarding_rules_protocol"),
        "port_forwarding_rules",
        ["protocol"],
    )
    op.create_index(
        op.f("ix_port_forwarding_rules_router_device_id"),
        "port_forwarding_rules",
        ["router_device_id"],
    )

    op.create_table(
        "ssid_access_points",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ssid_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["ssid_id"], ["ssids.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "ssid_id",
            "device_id",
            name="uq_ssid_access_points_ssid_id_device_id",
        ),
    )
    op.create_index(
        op.f("ix_ssid_access_points_device_id"),
        "ssid_access_points",
        ["device_id"],
    )
    op.create_index(op.f("ix_ssid_access_points_id"), "ssid_access_points", ["id"])
    op.create_index(
        op.f("ix_ssid_access_points_ssid_id"),
        "ssid_access_points",
        ["ssid_id"],
    )

    op.create_table(
        "cables",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cable_id", sa.String(length=4), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("from_port_id", sa.Integer(), nullable=True),
        sa.Column("to_port_id", sa.Integer(), nullable=True),
        sa.Column("cable_type", sa.String(length=100), nullable=True),
        sa.Column("length", sa.String(length=100), nullable=True),
        sa.Column("colour", sa.String(length=100), nullable=True),
        sa.Column("route_notes", sa.Text(), nullable=True),
        sa.Column("installed_date", sa.Date(), nullable=True),
        sa.Column("last_tested_status", sa.String(length=50), nullable=True),
        sa.Column("last_tested_date", sa.Date(), nullable=True),
        sa.Column("cable_supplied_by", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.Integer(), nullable=True),
        sa.CheckConstraint(
            "cable_id ~ '^[A-Z][0-9]{3}$'",
            name="ck_cables_cable_id_format",
        ),
        sa.CheckConstraint(
            "from_port_id IS NULL OR to_port_id IS NULL OR from_port_id <> to_port_id",
            name="ck_cables_ports_not_same",
        ),
        sa.ForeignKeyConstraint(["from_port_id"], ["device_ports.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["to_port_id"], ["device_ports.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cables_cable_id"), "cables", ["cable_id"], unique=True)
    op.create_index(op.f("ix_cables_from_port_id"), "cables", ["from_port_id"])
    op.create_index(op.f("ix_cables_id"), "cables", ["id"])
    op.create_index(op.f("ix_cables_location_id"), "cables", ["location_id"])
    op.create_index(op.f("ix_cables_status"), "cables", ["status"])
    op.create_index(op.f("ix_cables_to_port_id"), "cables", ["to_port_id"])

    op.create_index(
        "uq_cables_from_port_active",
        "cables",
        ["from_port_id"],
        unique=True,
        postgresql_where=sa.text("from_port_id IS NOT NULL AND is_deleted = false"),
    )
    op.create_index(
        "uq_cables_to_port_active",
        "cables",
        ["to_port_id"],
        unique=True,
        postgresql_where=sa.text("to_port_id IS NOT NULL AND is_deleted = false"),
    )


def downgrade() -> None:
    op.drop_index("uq_cables_to_port_active", table_name="cables")
    op.drop_index("uq_cables_from_port_active", table_name="cables")

    op.drop_index(op.f("ix_cables_to_port_id"), table_name="cables")
    op.drop_index(op.f("ix_cables_status"), table_name="cables")
    op.drop_index(op.f("ix_cables_location_id"), table_name="cables")
    op.drop_index(op.f("ix_cables_id"), table_name="cables")
    op.drop_index(op.f("ix_cables_from_port_id"), table_name="cables")
    op.drop_index(op.f("ix_cables_cable_id"), table_name="cables")
    op.drop_table("cables")

    op.drop_index(op.f("ix_ssid_access_points_ssid_id"), table_name="ssid_access_points")
    op.drop_index(op.f("ix_ssid_access_points_id"), table_name="ssid_access_points")
    op.drop_index(op.f("ix_ssid_access_points_device_id"), table_name="ssid_access_points")
    op.drop_table("ssid_access_points")

    op.drop_index(op.f("ix_port_forwarding_rules_router_device_id"), table_name="port_forwarding_rules")
    op.drop_index(op.f("ix_port_forwarding_rules_protocol"), table_name="port_forwarding_rules")
    op.drop_index(op.f("ix_port_forwarding_rules_is_enabled"), table_name="port_forwarding_rules")
    op.drop_index(op.f("ix_port_forwarding_rules_internal_ip_address"), table_name="port_forwarding_rules")
    op.drop_index(op.f("ix_port_forwarding_rules_id"), table_name="port_forwarding_rules")
    op.drop_table("port_forwarding_rules")

    op.drop_index(op.f("ix_device_ports_id"), table_name="device_ports")
    op.drop_index(op.f("ix_device_ports_device_id"), table_name="device_ports")
    op.drop_table("device_ports")

    op.drop_index(op.f("ix_ssids_vlan_id"), table_name="ssids")
    op.drop_index(op.f("ix_ssids_location_id"), table_name="ssids")
    op.drop_index(op.f("ix_ssids_id"), table_name="ssids")
    op.drop_table("ssids")

    op.drop_index(op.f("ix_devices_vlan_id"), table_name="devices")
    op.drop_index(op.f("ix_devices_status"), table_name="devices")
    op.drop_index(op.f("ix_devices_name"), table_name="devices")
    op.drop_index(op.f("ix_devices_location_id"), table_name="devices")
    op.drop_index(op.f("ix_devices_ip_address"), table_name="devices")
    op.drop_index(op.f("ix_devices_id"), table_name="devices")
    op.drop_index(op.f("ix_devices_device_type_id"), table_name="devices")
    op.drop_table("devices")

    op.drop_index(op.f("ix_vlans_location_id"), table_name="vlans")
    op.drop_index(op.f("ix_vlans_id"), table_name="vlans")
    op.drop_table("vlans")

    op.drop_index(op.f("ix_admin_notes_updated_by"), table_name="admin_notes")
    op.drop_index(op.f("ix_admin_notes_location_id"), table_name="admin_notes")
    op.drop_index(op.f("ix_admin_notes_id"), table_name="admin_notes")
    op.drop_index(op.f("ix_admin_notes_created_by"), table_name="admin_notes")
    op.drop_table("admin_notes")

    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")

    op.drop_index(op.f("ix_settings_setting_key"), table_name="settings")
    op.drop_index(op.f("ix_settings_id"), table_name="settings")
    op.drop_table("settings")

    op.drop_index(op.f("ix_locations_upstream_device_id"), table_name="locations")
    op.drop_index(op.f("ix_locations_parent_location_id"), table_name="locations")
    op.drop_index(op.f("ix_locations_name"), table_name="locations")
    op.drop_index(op.f("ix_locations_id"), table_name="locations")
    op.drop_table("locations")

    op.drop_index(op.f("ix_device_types_slug"), table_name="device_types")
    op.drop_index(op.f("ix_device_types_name"), table_name="device_types")
    op.drop_index(op.f("ix_device_types_id"), table_name="device_types")
    op.drop_table("device_types")

    op.drop_index(op.f("ix_audit_logs_user_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_entity_type"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_entity_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_created_at"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_action"), table_name="audit_logs")
    op.drop_table("audit_logs")
