from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class SSIDAccessPoint(Base, TimestampMixin):
    """
    Join table linking SSIDs to Access Point devices.

    A single SSID may be broadcast by multiple APs.
    A single AP may broadcast multiple SSIDs.
    """

    __tablename__ = "ssid_access_points"

    __table_args__ = (
        UniqueConstraint(
            "ssid_id",
            "device_id",
            name="uq_ssid_access_points_ssid_id_device_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    ssid_id: Mapped[int] = mapped_column(
        ForeignKey("ssids.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )