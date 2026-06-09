from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, SoftDeleteMixin, TimestampMixin


class SSID(Base, TimestampMixin, SoftDeleteMixin):
    """
    Wi-Fi network record.

    SSID passwords must be encrypted before being stored in
    encrypted_password.

    Users may view SSIDs but must not view passwords.
    Admin password reveals must be audit logged.
    """

    __tablename__ = "ssids"

    __table_args__ = (
        UniqueConstraint("location_id", "name", name="uq_ssids_location_id_name"),
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

    encrypted_password: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    security_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    vlan_id: Mapped[int | None] = mapped_column(
        ForeignKey("vlans.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )