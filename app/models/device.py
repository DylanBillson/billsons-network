from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TimestampMixin


class Device(Base, TimestampMixin, SoftDeleteMixin):
    """
    Network device.

    Device names must be globally unique across all locations.
    """

    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    device_type_id: Mapped[int] = mapped_column(
        ForeignKey("device_types.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    manufacturer: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    model: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    serial_number: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    mac_address: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    ip_assignment_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    vlan_id: Mapped[int | None] = mapped_column(
        ForeignKey("vlans.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    power_source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="external_power",
    )

    supplied_by: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    purchase_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
        index=True,
    )

    photo_path: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    location = relationship(
        "Location",
        foreign_keys=[location_id],
    )

    device_type = relationship(
        "DeviceType",
        foreign_keys=[device_type_id],
    )

    vlan = relationship(
        "VLAN",
        foreign_keys=[vlan_id],
    )

    ports = relationship(
        "DevicePort",
        back_populates="device",
        order_by="DevicePort.sort_order",
    )