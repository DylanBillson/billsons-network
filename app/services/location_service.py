from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.admin_note import AdminNote
from app.models.cable import Cable
from app.models.device import Device
from app.models.location import Location
from app.models.ssid import SSID
from app.models.vlan import VLAN


class LocationService:
    @staticmethod
    def list_locations(db: Session) -> list[Location]:
        return list(
            db.scalars(
                select(Location).order_by(Location.name.asc())
            )
        )

    @staticmethod
    def get_location(db: Session, location_id: int) -> Location | None:
        return db.get(Location, location_id)

    @staticmethod
    def create_location(
        db: Session,
        *,
        name: str,
        description: str | None = None,
        notes: str | None = None,
        address: str | None = None,
        parent_location_id: int | None = None,
        upstream_device_id: int | None = None,
    ) -> Location:
        name = name.strip()

        if not name:
            raise ValueError("Location name is required.")

        existing = db.scalar(
            select(Location).where(
                func.lower(Location.name) == name.lower()
            )
        )

        if existing:
            raise ValueError("A location with this name already exists.")

        location = Location(
            name=name,
            description=description.strip() if description else None,
            notes=notes.strip() if notes else None,
            address=address.strip() if address else None,
            parent_location_id=parent_location_id,
            upstream_device_id=upstream_device_id,
        )

        db.add(location)
        db.commit()
        db.refresh(location)

        return location

    @staticmethod
    def update_location(
        db: Session,
        *,
        location: Location,
        name: str,
        description: str | None = None,
        notes: str | None = None,
        address: str | None = None,
        parent_location_id: int | None = None,
        upstream_device_id: int | None = None,
    ) -> Location:
        name = name.strip()

        if not name:
            raise ValueError("Location name is required.")

        existing = db.scalar(
            select(Location).where(
                func.lower(Location.name) == name.lower(),
                Location.id != location.id,
            )
        )

        if existing:
            raise ValueError("A location with this name already exists.")

        if parent_location_id == location.id:
            raise ValueError("A location cannot be its own parent.")

        location.name = name
        location.description = description.strip() if description else None
        location.notes = notes.strip() if notes else None
        location.address = address.strip() if address else None
        location.parent_location_id = parent_location_id
        location.upstream_device_id = upstream_device_id

        db.add(location)
        db.commit()
        db.refresh(location)

        return location

    @staticmethod
    def get_delete_blockers(db: Session, location: Location) -> list[str]:
        blockers: list[str] = []

        child_count = db.scalar(
            select(func.count(Location.id)).where(
                Location.parent_location_id == location.id
            )
        )

        device_count = db.scalar(
            select(func.count(Device.id)).where(
                Device.location_id == location.id,
                Device.is_deleted.is_(False),
            )
        )

        cable_count = db.scalar(
            select(func.count(Cable.id)).where(
                Cable.location_id == location.id,
                Cable.is_deleted.is_(False),
            )
        )

        vlan_count = db.scalar(
            select(func.count(VLAN.id)).where(
                VLAN.location_id == location.id,
                VLAN.is_deleted.is_(False),
            )
        )

        ssid_count = db.scalar(
            select(func.count(SSID.id)).where(
                SSID.location_id == location.id,
                SSID.is_deleted.is_(False),
            )
        )

        note_count = db.scalar(
            select(func.count(AdminNote.id)).where(
                AdminNote.location_id == location.id,
                AdminNote.is_deleted.is_(False),
            )
        )

        if child_count:
            blockers.append(f"{child_count} child location(s)")

        if device_count:
            blockers.append(f"{device_count} device(s)")

        if cable_count:
            blockers.append(f"{cable_count} cable(s)")

        if vlan_count:
            blockers.append(f"{vlan_count} VLAN(s)")

        if ssid_count:
            blockers.append(f"{ssid_count} SSID(s)")

        if note_count:
            blockers.append(f"{note_count} admin note(s)")

        return blockers

    @staticmethod
    def delete_location(db: Session, location: Location) -> None:
        blockers = LocationService.get_delete_blockers(db, location)

        if blockers:
            raise ValueError(
                "Cannot delete location. Please remove: "
                + ", ".join(blockers)
                + "."
            )

        db.delete(location)
        db.commit()