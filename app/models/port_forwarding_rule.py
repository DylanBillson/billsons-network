from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TimestampMixin

class PortForwardingRule(Base, TimestampMixin, SoftDeleteMixin):
    """
    Router port forwarding documentation.

    Only Router device types should have port forwarding rules.
    That rule should be enforced in application logic.
    """

    __tablename__ = "port_forwarding_rules"

    __table_args__ = (
        CheckConstraint(
            "external_port_start BETWEEN 1 AND 65535",
            name="ck_port_forwarding_external_port_start_range",
        ),
        CheckConstraint(
            "external_port_end IS NULL OR external_port_end BETWEEN 1 AND 65535",
            name="ck_port_forwarding_external_port_end_range",
        ),
        CheckConstraint(
            "internal_port_start BETWEEN 1 AND 65535",
            name="ck_port_forwarding_internal_port_start_range",
        ),
        CheckConstraint(
            "internal_port_end IS NULL OR internal_port_end BETWEEN 1 AND 65535",
            name="ck_port_forwarding_internal_port_end_range",
        ),
        CheckConstraint(
            "external_port_end IS NULL OR external_port_end >= external_port_start",
            name="ck_port_forwarding_external_port_order",
        ),
        CheckConstraint(
            "internal_port_end IS NULL OR internal_port_end >= internal_port_start",
            name="ck_port_forwarding_internal_port_order",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    router_device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    rule_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    external_port_start: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    external_port_end: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    internal_ip_address: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    internal_port_start: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    internal_port_end: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    protocol: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    router_device = relationship(
        "Device",
        foreign_keys=[router_device_id],
    )