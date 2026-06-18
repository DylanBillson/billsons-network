import re
from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.cable import Cable
from app.models.device import Device
from app.models.device_port import DevicePort
from app.models.location import Location


VALID_CABLE_ID_PATTERN = re.compile(r"^[A-Z][0-9]{3}$")

VALID_CABLE_STATUSES = {
    "active",
    "inactive",
    "retired",
}

VALID_TEST_STATUSES = {
    "",
    "pass",
    "fail",
    "not_tested",
}


class CableService:
    @staticmethod
    def list_cables(
        db: Session,
        *,
        location_id: int | None = None,
    ) -> list[Cable]:
        query = (
            select(Cable)
            .options(
                selectinload(Cable.location),
                selectinload(Cable.from_port).selectinload(DevicePort.device),
                selectinload(Cable.to_port).selectinload(DevicePort.device),
            )
            .where(Cable.is_deleted.is_(False))
        )

        if location_id is not None:
            query = query.where(Cable.location_id == location_id)

        query = query.order_by(Cable.cable_id.asc())

        return list(db.scalars(query))

    @staticmethod
    def get_cable(
        db: Session,
        cable_id: int,
    ) -> Cable | None:
        return db.scalar(
            select(Cable)
            .options(
                selectinload(Cable.location),
                selectinload(Cable.from_port).selectinload(DevicePort.device),
                selectinload(Cable.to_port).selectinload(DevicePort.device),
            )
            .where(
                Cable.id == cable_id,
                Cable.is_deleted.is_(False),
            )
        )

    @staticmethod
    def get_port_cable(
        db: Session,
        port_id: int,
    ) -> Cable | None:
        return db.scalar(
            select(Cable)
            .options(
                selectinload(Cable.from_port).selectinload(DevicePort.device),
                selectinload(Cable.to_port).selectinload(DevicePort.device),
            )
            .where(
                Cable.is_deleted.is_(False),
                or_(
                    Cable.from_port_id == port_id,
                    Cable.to_port_id == port_id,
                ),
            )
        )

    @staticmethod
    def get_device_cable_map(
        db: Session,
        device_id: int,
    ) -> dict[int, Cable]:
        cables = list(
            db.scalars(
                select(Cable)
                .options(
                    selectinload(Cable.from_port).selectinload(DevicePort.device),
                    selectinload(Cable.to_port).selectinload(DevicePort.device),
                )
                .join(
                    DevicePort,
                    or_(
                        Cable.from_port_id == DevicePort.id,
                        Cable.to_port_id == DevicePort.id,
                    ),
                )
                .where(
                    Cable.is_deleted.is_(False),
                    DevicePort.device_id == device_id,
                )
            )
        )

        port_cable_map: dict[int, Cable] = {}

        for cable in cables:
            if cable.from_port_id is not None:
                port_cable_map[cable.from_port_id] = cable

            if cable.to_port_id is not None:
                port_cable_map[cable.to_port_id] = cable

        return port_cable_map

    @staticmethod
    def get_other_port(
        cable: Cable,
        port: DevicePort,
    ) -> DevicePort | None:
        if cable.from_port_id == port.id:
            return cable.to_port

        if cable.to_port_id == port.id:
            return cable.from_port

        return None

    @staticmethod
    def list_devices_for_location(
        db: Session,
        location_id: int,
    ) -> list[Device]:
        return list(
            db.scalars(
                select(Device)
                .where(
                    Device.location_id == location_id,
                    Device.is_deleted.is_(False),
                )
                .order_by(Device.name.asc())
            )
        )

    @staticmethod
    def list_ports_for_location(
        db: Session,
        location_id: int,
    ) -> list[DevicePort]:
        return list(
            db.scalars(
                select(DevicePort)
                .join(Device, Device.id == DevicePort.device_id)
                .options(selectinload(DevicePort.device))
                .where(
                    Device.location_id == location_id,
                    Device.is_deleted.is_(False),
                )
                .order_by(
                    Device.name.asc(),
                    DevicePort.sort_order.asc(),
                )
            )
        )

    @staticmethod
    def port_is_in_use(
        db: Session,
        port_id: int,
        *,
        excluding_cable_id: int | None = None,
    ) -> bool:
        query = select(Cable).where(
            Cable.is_deleted.is_(False),
            or_(
                Cable.from_port_id == port_id,
                Cable.to_port_id == port_id,
            ),
        )

        if excluding_cable_id is not None:
            query = query.where(Cable.id != excluding_cable_id)

        return db.scalar(query) is not None

    @staticmethod
    def validate_port(
        db: Session,
        *,
        port_id: int | None,
        location_id: int,
        label: str,
        excluding_cable_id: int | None = None,
    ) -> DevicePort | None:
        if port_id is None:
            return None

        port = db.scalar(
            select(DevicePort)
            .join(Device, Device.id == DevicePort.device_id)
            .where(
                DevicePort.id == port_id,
                Device.location_id == location_id,
                Device.is_deleted.is_(False),
            )
        )

        if port is None:
            raise ValueError(f"{label} port does not exist in this location.")

        if CableService.port_is_in_use(
            db,
            port_id,
            excluding_cable_id=excluding_cable_id,
        ):
            raise ValueError(f"{label} port is already connected to another cable.")

        return port

    @staticmethod
    def create_cable(
        db: Session,
        *,
        cable_id: str,
        location_id: int,
        from_port_id: int | None = None,
        to_port_id: int | None = None,
        cable_type: str | None = None,
        length: str | None = None,
        colour: str | None = None,
        route_notes: str | None = None,
        installed_date: date | None = None,
        last_tested_status: str | None = None,
        last_tested_date: date | None = None,
        cable_supplied_by: str | None = None,
        status: str = "active",
    ) -> Cable:
        cable_id = cable_id.strip().upper()

        if not VALID_CABLE_ID_PATTERN.match(cable_id):
            raise ValueError(
                "Cable ID must be one uppercase letter followed by three numbers, for example X305."
            )

        existing = db.scalar(
            select(Cable).where(
                func.upper(Cable.cable_id) == cable_id,
                Cable.is_deleted.is_(False),
            )
        )

        if existing:
            raise ValueError("A cable with this ID already exists.")

        location = db.get(Location, location_id)

        if location is None:
            raise ValueError("Selected location does not exist.")

        if status not in VALID_CABLE_STATUSES:
            raise ValueError("Invalid cable status.")

        if last_tested_status is None:
            last_tested_status = ""

        if last_tested_status not in VALID_TEST_STATUSES:
            raise ValueError("Invalid test status.")

        if from_port_id and to_port_id and from_port_id == to_port_id:
            raise ValueError("A cable cannot connect a port to itself.")

        CableService.validate_port(
            db,
            port_id=from_port_id,
            location_id=location_id,
            label="From",
        )

        CableService.validate_port(
            db,
            port_id=to_port_id,
            location_id=location_id,
            label="To",
        )

        cable = Cable(
            cable_id=cable_id,
            location_id=location_id,
            from_port_id=from_port_id,
            to_port_id=to_port_id,
            cable_type=cable_type.strip() if cable_type else None,
            length=length.strip() if length else None,
            colour=colour.strip() if colour else None,
            route_notes=route_notes.strip() if route_notes else None,
            installed_date=installed_date,
            last_tested_status=last_tested_status or None,
            last_tested_date=last_tested_date,
            cable_supplied_by=cable_supplied_by.strip() if cable_supplied_by else None,
            status=status,
        )

        db.add(cable)
        db.commit()
        db.refresh(cable)

        return cable

    @staticmethod
    def update_cable(
        db: Session,
        *,
        cable: Cable,
        cable_id: str,
        from_port_id: int | None = None,
        to_port_id: int | None = None,
        cable_type: str | None = None,
        length: str | None = None,
        colour: str | None = None,
        route_notes: str | None = None,
        installed_date: date | None = None,
        last_tested_status: str | None = None,
        last_tested_date: date | None = None,
        cable_supplied_by: str | None = None,
        status: str = "active",
    ) -> Cable:
        cable_id = cable_id.strip().upper()

        if not VALID_CABLE_ID_PATTERN.match(cable_id):
            raise ValueError(
                "Cable ID must be one uppercase letter followed by three numbers, for example X305."
            )

        existing = db.scalar(
            select(Cable).where(
                func.upper(Cable.cable_id) == cable_id,
                Cable.id != cable.id,
                Cable.is_deleted.is_(False),
            )
        )

        if existing:
            raise ValueError("A cable with this ID already exists.")

        if status not in VALID_CABLE_STATUSES:
            raise ValueError("Invalid cable status.")

        if last_tested_status is None:
            last_tested_status = ""

        if last_tested_status not in VALID_TEST_STATUSES:
            raise ValueError("Invalid test status.")

        if from_port_id and to_port_id and from_port_id == to_port_id:
            raise ValueError("A cable cannot connect a port to itself.")

        CableService.validate_port(
            db,
            port_id=from_port_id,
            location_id=cable.location_id,
            label="From",
            excluding_cable_id=cable.id,
        )

        CableService.validate_port(
            db,
            port_id=to_port_id,
            location_id=cable.location_id,
            label="To",
            excluding_cable_id=cable.id,
        )

        cable.cable_id = cable_id
        cable.from_port_id = from_port_id
        cable.to_port_id = to_port_id
        cable.cable_type = cable_type.strip() if cable_type else None
        cable.length = length.strip() if length else None
        cable.colour = colour.strip() if colour else None
        cable.route_notes = route_notes.strip() if route_notes else None
        cable.installed_date = installed_date
        cable.last_tested_status = last_tested_status or None
        cable.last_tested_date = last_tested_date
        cable.cable_supplied_by = cable_supplied_by.strip() if cable_supplied_by else None
        cable.status = status

        db.add(cable)
        db.commit()
        db.refresh(cable)

        return cable

    @staticmethod
    def delete_cable(
        db: Session,
        cable: Cable,
    ) -> None:
        cable.is_deleted = True
        cable.from_port_id = None
        cable.to_port_id = None

        db.add(cable)
        db.commit()