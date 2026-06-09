from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Convert class names to lowercase snake_case table names.

        Example:
            AuditLog -> audit_log

        Most final model table names should be explicitly set where plural names
        are preferred, e.g. __tablename__ = "audit_logs".
        """
        name = cls.__name__
        return "".join(
            ["_" + char.lower() if char.isupper() else char for char in name]
        ).lstrip("_")


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    deleted_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )


def utc_now() -> datetime:
    return datetime.now(timezone.utc)