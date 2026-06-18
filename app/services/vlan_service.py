from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.device import Device
from app.models.location import Location
from app.models.ssid import SSID
from app.models.vlan import VLAN


class VLANService:
    @staticmethod
    def list_vlans(
        db: Session,
        *,
        location_id: int | None = None,
    ) -> list[VLAN]:
        query = (
            select(VLAN)
            .options(
                selectinload(VLAN.location),
            )
            .where(
                VLAN.is_deleted.is_(False),
            )
        )

        if location_id is not None:
            query = query.where(
                VLAN.location_id == location_id,
            )

        query = query.order_by(
            VLAN.vlan_number.asc(),
            VLAN.name.asc(),
        )

        return list(db.scalars(query))

    @staticmethod
    def get_vlan(
        db: Session,
        vlan_id: int,
    ) -> VLAN | None:
        return db.scalar(
            select(VLAN)
            .options(
                selectinload(VLAN.location),
            )
            .where(
                VLAN.id == vlan_id,
                VLAN.is_deleted.is_(False),
            )
        )

    @staticmethod
    def create_vlan(
        db: Session,
        *,
        location_id: int,
        name: str,
        vlan_number: int,
        purpose: str | None = None,
        subnet: str | None = None,
        gateway: str | None = None,
        dhcp_range_start: str | None = None,
        dhcp_range_end: str | None = None,
        dns_settings: str | None = None,
        firewall_notes: str | None = None,
        allowed_access_rules: str | None = None,
    ) -> VLAN:
        name = name.strip()

        if not name:
            raise ValueError("VLAN name is required.")

        if vlan_number < 1 or vlan_number > 4094:
            raise ValueError("VLAN ID must be between 1 and 4094.")

        location = db.get(Location, location_id)

        if location is None:
            raise ValueError("Selected location does not exist.")

        existing_number = db.scalar(
            select(VLAN).where(
                VLAN.location_id == location_id,
                VLAN.vlan_number == vlan_number,
                VLAN.is_deleted.is_(False),
            )
        )

        if existing_number:
            raise ValueError("A VLAN with this ID already exists in this location.")

        existing_name = db.scalar(
            select(VLAN).where(
                VLAN.location_id == location_id,
                func.lower(VLAN.name) == name.lower(),
                VLAN.is_deleted.is_(False),
            )
        )

        if existing_name:
            raise ValueError("A VLAN with this name already exists in this location.")

        vlan = VLAN(
            location_id=location_id,
            name=name,
            vlan_number=vlan_number,
            purpose=purpose.strip() if purpose else None,
            subnet=subnet.strip() if subnet else None,
            gateway=gateway.strip() if gateway else None,
            dhcp_range_start=dhcp_range_start.strip() if dhcp_range_start else None,
            dhcp_range_end=dhcp_range_end.strip() if dhcp_range_end else None,
            dns_settings=dns_settings.strip() if dns_settings else None,
            firewall_notes=firewall_notes.strip() if firewall_notes else None,
            allowed_access_rules=allowed_access_rules.strip()
            if allowed_access_rules
            else None,
        )

        db.add(vlan)
        db.commit()
        db.refresh(vlan)

        return vlan

    @staticmethod
    def update_vlan(
        db: Session,
        *,
        vlan: VLAN,
        name: str,
        vlan_number: int,
        purpose: str | None = None,
        subnet: str | None = None,
        gateway: str | None = None,
        dhcp_range_start: str | None = None,
        dhcp_range_end: str | None = None,
        dns_settings: str | None = None,
        firewall_notes: str | None = None,
        allowed_access_rules: str | None = None,
    ) -> VLAN:
        name = name.strip()

        if not name:
            raise ValueError("VLAN name is required.")

        if vlan_number < 1 or vlan_number > 4094:
            raise ValueError("VLAN ID must be between 1 and 4094.")

        existing_number = db.scalar(
            select(VLAN).where(
                VLAN.location_id == vlan.location_id,
                VLAN.vlan_number == vlan_number,
                VLAN.id != vlan.id,
                VLAN.is_deleted.is_(False),
            )
        )

        if existing_number:
            raise ValueError("A VLAN with this ID already exists in this location.")

        existing_name = db.scalar(
            select(VLAN).where(
                VLAN.location_id == vlan.location_id,
                func.lower(VLAN.name) == name.lower(),
                VLAN.id != vlan.id,
                VLAN.is_deleted.is_(False),
            )
        )

        if existing_name:
            raise ValueError("A VLAN with this name already exists in this location.")

        vlan.name = name
        vlan.vlan_number = vlan_number
        vlan.purpose = purpose.strip() if purpose else None
        vlan.subnet = subnet.strip() if subnet else None
        vlan.gateway = gateway.strip() if gateway else None
        vlan.dhcp_range_start = dhcp_range_start.strip() if dhcp_range_start else None
        vlan.dhcp_range_end = dhcp_range_end.strip() if dhcp_range_end else None
        vlan.dns_settings = dns_settings.strip() if dns_settings else None
        vlan.firewall_notes = firewall_notes.strip() if firewall_notes else None
        vlan.allowed_access_rules = (
            allowed_access_rules.strip() if allowed_access_rules else None
        )

        db.add(vlan)
        db.commit()
        db.refresh(vlan)

        return vlan

    @staticmethod
    def get_delete_blockers(
        db: Session,
        vlan: VLAN,
    ) -> list[str]:
        device_count = db.scalar(
            select(func.count(Device.id)).where(
                Device.vlan_id == vlan.id,
                Device.is_deleted.is_(False),
            )
        )

        ssid_count = db.scalar(
            select(func.count(SSID.id)).where(
                SSID.vlan_id == vlan.id,
                SSID.is_deleted.is_(False),
            )
        )

        blockers: list[str] = []

        if device_count:
            blockers.append(f"{device_count} device(s)")

        if ssid_count:
            blockers.append(f"{ssid_count} SSID(s)")

        return blockers

    @staticmethod
    def delete_vlan(
        db: Session,
        vlan: VLAN,
    ) -> None:
        blockers = VLANService.get_delete_blockers(
            db,
            vlan,
        )

        if blockers:
            raise ValueError(
                "Cannot delete VLAN. Please remove or reassign: "
                + ", ".join(blockers)
                + "."
            )

        vlan.is_deleted = True

        db.add(vlan)
        db.commit()