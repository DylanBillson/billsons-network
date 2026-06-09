from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Location(Base, TimestampMixin):
    """
    Physical or logical network location.

    Examples:
        - Main Office
        - Pub
        - Hotel
        - Flat
        - Warehouse
        - Remote Site

    Locations do not have active/inactive status.
    If a location is no longer required, it should be deleted after
    dependent records have been removed or reassigned.
    """

    __tablename__ = "locations"

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

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    parent_location_id: Mapped[int | None] = mapped_column(
        ForeignKey("locations.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    upstream_device_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )