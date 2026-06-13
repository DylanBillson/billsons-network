from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.device import Device
from app.models.device_port import DevicePort
from app.models.device_type import DeviceType
from app.models.location import Location
from app.models.vlan import VLAN


VALID_DEVICE_STATUSES = {
    "active",
    "inactive",
    "retired",
    "faulty",
}

VALID_POWER_SOURCES = {
    "external_power",
    "poe_powered",
}

VALID_IP_ASSIGNMENT_TYPES = {
    "static",
    "reserved",
    "dhcp",
}


class DeviceService:
    @staticmethod
    def list_devices(
        db: Session,
        *,
        location_id: int | None = None,
    ) -> list[Device]:
        query = (
            select(Device)
            .options(
                selectinload(Device.device_type),
                selectinload(Device.vlan),
            )
            .where(
                Device.is_deleted.is_(False),
            )
        )

        if location_id is not None:
            query = query.where(
                Device.location_id == location_id,
            )

        query = query.order_by(
            Device.name.asc(),
        )

        return list(db.scalars(query))

    @staticmethod
    def get_device(
        db: Session,
        device_id: int,
    ) -> Device | None:
        device = db.scalar(
            select(Device)
            .options(
                selectinload(Device.location),
                selectinload(Device.device_type),
                selectinload(Device.vlan),
            )
            .where(
                Device.id == device_id,
                Device.is_deleted.is_(False),
            )
        )

        return device

    @staticmethod
    def get_device_with_ports(
        db: Session,
        device_id: int,
    ) -> Device | None:
        device = db.scalar(
            select(Device)
            .options(
                selectinload(Device.location),
                selectinload(Device.device_type),
                selectinload(Device.vlan),
                selectinload(Device.ports),
            )
            .where(
                Device.id == device_id,
                Device.is_deleted.is_(False),
            )
        )

        return device

    @staticmethod
    def list_ports_for_device(
        db: Session,
        device_id: int,
    ) -> list[DevicePort]:
        return list(
            db.scalars(
                select(DevicePort)
                .where(
                    DevicePort.device_id == device_id,
                )
                .order_by(DevicePort.sort_order.asc())
            )
        )

    @staticmethod
    def list_device_types(db: Session) -> list[DeviceType]:
        return list(
            db.scalars(
                select(DeviceType)
                .where(
                    DeviceType.is_deleted.is_(False),
                    DeviceType.is_active.is_(True),
                )
                .order_by(DeviceType.name.asc())
            )
        )

    @staticmethod
    def list_vlans_for_location(
        db: Session,
        location_id: int,
    ) -> list[VLAN]:
        return list(
            db.scalars(
                select(VLAN)
                .where(
                    VLAN.location_id == location_id,
                    VLAN.is_deleted.is_(False),
                )
                .order_by(VLAN.vlan_number.asc())
            )
        )

    @staticmethod
    def create_device(
        db: Session,
        *,
        name: str,
        location_id: int,
        device_type_id: int,
        manufacturer: str | None = None,
        model: str | None = None,
        serial_number: str | None = None,
        mac_address: str | None = None,
        ip_assignment_type: str | None = None,
        ip_address: str | None = None,
        vlan_id: int | None = None,
        power_source: str = "external_power",
        supplied_by: str | None = None,
        purchase_date=None,
        notes: str | None = None,
        status: str = "active",
        photo_path: str | None = None,
        port_count: int = 0,
    ) -> Device:
        name = name.strip()

        if not name:
            raise ValueError("Device name is required.")

        existing = db.scalar(
            select(Device).where(
                func.lower(Device.name) == name.lower(),
                Device.is_deleted.is_(False),
            )
        )

        if existing:
            raise ValueError("A device with this name already exists.")

        location = db.get(Location, location_id)

        if location is None:
            raise ValueError("Selected location does not exist.")

        device_type = db.get(DeviceType, device_type_id)

        if device_type is None or device_type.is_deleted or not device_type.is_active:
            raise ValueError("Selected device type does not exist or is inactive.")

        if status not in VALID_DEVICE_STATUSES:
            raise ValueError("Invalid device status.")

        if power_source not in VALID_POWER_SOURCES:
            raise ValueError("Invalid power source.")

        if ip_assignment_type:
            if ip_assignment_type not in VALID_IP_ASSIGNMENT_TYPES:
                raise ValueError("Invalid IP assignment type.")
        else:
            ip_assignment_type = None

        if vlan_id is not None:
            vlan = db.get(VLAN, vlan_id)

            if vlan is None or vlan.is_deleted:
                raise ValueError("Selected VLAN does not exist.")

            if vlan.location_id != location_id:
                raise ValueError("Selected VLAN does not belong to this location.")

        if port_count < 0:
            raise ValueError("Port count cannot be negative.")

        device = Device(
            name=name,
            location_id=location_id,
            device_type_id=device_type_id,
            manufacturer=manufacturer.strip() if manufacturer else None,
            model=model.strip() if model else None,
            serial_number=serial_number.strip() if serial_number else None,
            mac_address=mac_address.strip() if mac_address else None,
            ip_assignment_type=ip_assignment_type,
            ip_address=ip_address.strip() if ip_address else None,
            vlan_id=vlan_id,
            power_source=power_source,
            supplied_by=supplied_by.strip() if supplied_by else None,
            purchase_date=purchase_date,
            notes=notes.strip() if notes else None,
            status=status,
            photo_path=photo_path,
        )

        db.add(device)
        db.flush()

        for port_number in range(1, port_count + 1):
            db.add(
                DevicePort(
                    device_id=device.id,
                    label=str(port_number),
                    sort_order=port_number,
                )
            )

        db.commit()
        db.refresh(device)

        return device

    @staticmethod
    def update_device(
        db: Session,
        *,
        device: Device,
        name: str,
        location_id: int,
        device_type_id: int,
        manufacturer: str | None = None,
        model: str | None = None,
        serial_number: str | None = None,
        mac_address: str | None = None,
        ip_assignment_type: str | None = None,
        ip_address: str | None = None,
        vlan_id: int | None = None,
        power_source: str = "external_power",
        supplied_by: str | None = None,
        purchase_date=None,
        notes: str | None = None,
        status: str = "active",
        photo_path: str | None = None,
    ) -> Device:
        name = name.strip()

        if not name:
            raise ValueError("Device name is required.")

        existing = db.scalar(
            select(Device).where(
                func.lower(Device.name) == name.lower(),
                Device.id != device.id,
                Device.is_deleted.is_(False),
            )
        )

        if existing:
            raise ValueError("A device with this name already exists.")

        location = db.get(Location, location_id)

        if location is None:
            raise ValueError("Selected location does not exist.")

        device_type = db.get(DeviceType, device_type_id)

        if device_type is None or device_type.is_deleted or not device_type.is_active:
            raise ValueError("Selected device type does not exist or is inactive.")

        if status not in VALID_DEVICE_STATUSES:
            raise ValueError("Invalid device status.")

        if power_source not in VALID_POWER_SOURCES:
            raise ValueError("Invalid power source.")

        if ip_assignment_type:
            if ip_assignment_type not in VALID_IP_ASSIGNMENT_TYPES:
                raise ValueError("Invalid IP assignment type.")
        else:
            ip_assignment_type = None

        if vlan_id is not None:
            vlan = db.get(VLAN, vlan_id)

            if vlan is None or vlan.is_deleted:
                raise ValueError("Selected VLAN does not exist.")

            if vlan.location_id != location_id:
                raise ValueError("Selected VLAN does not belong to this location.")

        device.name = name
        device.location_id = location_id
        device.device_type_id = device_type_id
        device.manufacturer = manufacturer.strip() if manufacturer else None
        device.model = model.strip() if model else None
        device.serial_number = serial_number.strip() if serial_number else None
        device.mac_address = mac_address.strip() if mac_address else None
        device.ip_assignment_type = ip_assignment_type
        device.ip_address = ip_address.strip() if ip_address else None
        device.vlan_id = vlan_id
        device.power_source = power_source
        device.supplied_by = supplied_by.strip() if supplied_by else None
        device.purchase_date = purchase_date
        device.notes = notes.strip() if notes else None
        device.status = status

        if photo_path is not None:
            device.photo_path = photo_path

        db.add(device)
        db.commit()
        db.refresh(device)

        return device

    @staticmethod
    def get_delete_blockers(
        db: Session,
        device: Device,
    ) -> list[str]:
        port_count = db.scalar(
            select(func.count(DevicePort.id)).where(
                DevicePort.device_id == device.id,
            )
        )

        blockers: list[str] = []

        if port_count:
            blockers.append(f"{port_count} port(s)")

        return blockers

    @staticmethod
    def delete_device(
        db: Session,
        device: Device,
    ) -> None:
        blockers = DeviceService.get_delete_blockers(db, device)

        if blockers:
            raise ValueError(
                "Cannot delete device. Please remove: "
                + ", ".join(blockers)
                + "."
            )

        device.is_deleted = True

        db.add(device)
        db.commit()