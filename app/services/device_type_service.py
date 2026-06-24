from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.device import Device
from app.models.device_type import DeviceType


class DeviceTypeService:
    @staticmethod
    def list_device_types(
        db: Session,
        *,
        include_inactive: bool = False,
    ) -> list[DeviceType]:
        query = select(DeviceType)

        if not include_inactive:
            query = query.where(
                DeviceType.is_active.is_(True),
            )

        query = query.order_by(
            DeviceType.name.asc(),
        )

        return list(
            db.scalars(query)
        )

    @staticmethod
    def get_device_type(
        db: Session,
        device_type_id: int,
    ) -> DeviceType | None:
        return db.get(
            DeviceType,
            device_type_id,
        )

    @staticmethod
    def create_device_type(
        db: Session,
        *,
        name: str,
        slug: str,
        description: str | None = None,
        icon_path: str | None = None,
        is_default: bool = False,
        is_active: bool = True,
    ) -> DeviceType:
        name = name.strip()
        slug = slug.strip().lower()

        if not name:
            raise ValueError(
                "Name is required."
            )

        if not slug:
            raise ValueError(
                "Slug is required."
            )

        existing_name = db.scalar(
            select(DeviceType).where(
                func.lower(DeviceType.name) == name.lower(),
            )
        )

        if existing_name:
            raise ValueError(
                "A device type with that name already exists."
            )

        existing_slug = db.scalar(
            select(DeviceType).where(
                func.lower(DeviceType.slug) == slug.lower(),
            )
        )

        if existing_slug:
            raise ValueError(
                "A device type with that slug already exists."
            )

        device_type = DeviceType(
            name=name,
            slug=slug,
            description=description or None,
            icon_path=icon_path or None,
            is_default=is_default,
            is_active=is_active,
        )

        db.add(device_type)
        db.commit()
        db.refresh(device_type)

        return device_type

    @staticmethod
    def update_device_type(
        db: Session,
        *,
        device_type: DeviceType,
        name: str,
        slug: str,
        description: str | None = None,
        icon_path: str | None = None,
        is_default: bool = False,
        is_active: bool = True,
    ) -> DeviceType:
        name = name.strip()
        slug = slug.strip().lower()

        if not name:
            raise ValueError(
                "Name is required."
            )

        if not slug:
            raise ValueError(
                "Slug is required."
            )

        existing_name = db.scalar(
            select(DeviceType).where(
                func.lower(DeviceType.name) == name.lower(),
                DeviceType.id != device_type.id,
            )
        )

        if existing_name:
            raise ValueError(
                "A device type with that name already exists."
            )

        existing_slug = db.scalar(
            select(DeviceType).where(
                func.lower(DeviceType.slug) == slug.lower(),
                DeviceType.id != device_type.id,
            )
        )

        if existing_slug:
            raise ValueError(
                "A device type with that slug already exists."
            )

        device_type.name = name
        device_type.slug = slug
        device_type.description = description or None
        device_type.icon_path = icon_path or None
        device_type.is_default = is_default
        device_type.is_active = is_active

        db.add(device_type)
        db.commit()
        db.refresh(device_type)

        return device_type

    @staticmethod
    def delete_device_type(
        db: Session,
        device_type: DeviceType,
    ) -> None:
        device_count = db.scalar(
            select(func.count())
            .select_from(Device)
            .where(
                Device.device_type_id == device_type.id,
            )
        ) or 0

        if device_count > 0:
            raise ValueError(
                "Cannot delete a device type that is in use."
            )

        if device_type.is_default:
            raise ValueError(
                "Default device types cannot be deleted."
            )

        db.delete(device_type)
        db.commit()