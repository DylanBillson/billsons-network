from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class DevicePort(Base, TimestampMixin):
    """
    Port belonging to a device.

    Port labels must be unique within a device, but not globally.
    Example:
        Switch A -> Port 1
        Switch B -> Port 1
    """

    __tablename__ = "device_ports"

    __table_args__ = (
        UniqueConstraint(
            "device_id",
            "label",
            name="uq_device_ports_device_id_label",
        ),
        UniqueConstraint(
            "device_id",
            "sort_order",
            name="uq_device_ports_device_id_sort_order",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    label: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    vlan_id: Mapped[int | None] = mapped_column(
        ForeignKey("vlans.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    vlan_mode: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="none",
    )

    vlan_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    device = relationship(
        "Device",
        back_populates="ports",
    )

    vlan = relationship(
        "VLAN",
        foreign_keys=[vlan_id],
    )

    cables_from = relationship(
        "Cable",
        foreign_keys="Cable.from_port_id",
        overlaps="from_port",
    )

    cables_to = relationship(
        "Cable",
        foreign_keys="Cable.to_port_id",
        overlaps="to_port",
    )