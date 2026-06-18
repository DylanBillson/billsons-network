from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TimestampMixin


class Cable(Base, TimestampMixin, SoftDeleteMixin):
    """
    Physical cable record.

    Cables are the source of truth for physical port connections.

    Cable IDs must be globally unique and match:
        One uppercase letter followed by three numbers.
        Example: X305
    """

    __tablename__ = "cables"

    __table_args__ = (
        CheckConstraint(
            "cable_id ~ '^[A-Z][0-9]{3}$'",
            name="ck_cables_cable_id_format",
        ),
        CheckConstraint(
            "from_port_id IS NULL OR to_port_id IS NULL OR from_port_id <> to_port_id",
            name="ck_cables_ports_not_same",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    cable_id: Mapped[str] = mapped_column(
        String(4),
        unique=True,
        nullable=False,
        index=True,
    )

    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    from_port_id: Mapped[int | None] = mapped_column(
        ForeignKey("device_ports.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    to_port_id: Mapped[int | None] = mapped_column(
        ForeignKey("device_ports.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    cable_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    length: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    colour: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    route_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    installed_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    last_tested_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    last_tested_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    cable_supplied_by: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
        index=True,
    )

    location = relationship(
        "Location",
        foreign_keys=[location_id],
    )

    from_port = relationship(
        "DevicePort",
        foreign_keys=[from_port_id],
    )

    to_port = relationship(
        "DevicePort",
        foreign_keys=[to_port_id],
    )