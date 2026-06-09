from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, SoftDeleteMixin, TimestampMixin


class VLAN(Base, TimestampMixin, SoftDeleteMixin):
    """
    VLAN and subnet documentation.

    VLAN numbers and names must be unique within a location,
    but do not need to be globally unique.
    """

    __tablename__ = "vlans"

    __table_args__ = (
        UniqueConstraint("location_id", "vlan_number", name="uq_vlans_location_id_vlan_number"),
        UniqueConstraint("location_id", "name", name="uq_vlans_location_id_name"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    vlan_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    purpose: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    subnet: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    gateway: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    dhcp_range_start: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    dhcp_range_end: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    dns_settings: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    firewall_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    allowed_access_rules: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )