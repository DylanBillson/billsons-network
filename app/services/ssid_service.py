from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.security import decrypt_text, encrypt_text
from app.models.device import Device
from app.models.ssid import SSID
from app.models.ssid_access_point import SSIDAccessPoint
from app.models.vlan import VLAN


VALID_SECURITY_TYPES = {
    "",
    "open",
    "wpa2",
    "wpa3",
    "wpa2_wpa3",
}


class SSIDService:
    @staticmethod
    def list_ssids(
        db: Session,
        *,
        location_id: int | None = None,
    ) -> list[SSID]:
        query = (
            select(SSID)
            .options(
                selectinload(SSID.location),
                selectinload(SSID.vlan),
                selectinload(SSID.access_points)
                .selectinload(SSIDAccessPoint.device)
                .selectinload(Device.device_type),
            )
            .where(SSID.is_deleted.is_(False))
        )

        if location_id is not None:
            query = query.where(SSID.location_id == location_id)

        query = query.order_by(SSID.name.asc())

        return list(db.scalars(query))

    @staticmethod
    def get_ssid(
        db: Session,
        ssid_id: int,
    ) -> SSID | None:
        return db.scalar(
            select(SSID)
            .options(
                selectinload(SSID.location),
                selectinload(SSID.vlan),
                selectinload(SSID.access_points)
                .selectinload(SSIDAccessPoint.device)
                .selectinload(Device.device_type),
            )
            .where(
                SSID.id == ssid_id,
                SSID.is_deleted.is_(False),
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
                .order_by(
                    VLAN.vlan_number.asc(),
                    VLAN.name.asc(),
                )
            )
        )

    @staticmethod
    def create_ssid(
        db: Session,
        *,
        location_id: int,
        name: str,
        password: str | None = None,
        security_type: str | None = None,
        vlan_id: int | None = None,
        notes: str | None = None,
    ) -> SSID:
        name = name.strip()

        if not name:
            raise ValueError("SSID name is required.")

        security_type = security_type or ""

        if security_type not in VALID_SECURITY_TYPES:
            raise ValueError("Invalid security type.")

        existing = db.scalar(
            select(SSID).where(
                SSID.location_id == location_id,
                func.lower(SSID.name) == name.lower(),
                SSID.is_deleted.is_(False),
            )
        )

        if existing:
            raise ValueError("An SSID with this name already exists in this location.")

        if vlan_id is not None:
            vlan = db.get(VLAN, vlan_id)

            if vlan is None or vlan.is_deleted:
                raise ValueError("Selected VLAN does not exist.")

            if vlan.location_id != location_id:
                raise ValueError("Selected VLAN does not belong to this location.")

        ssid = SSID(
            location_id=location_id,
            name=name,
            encrypted_password=encrypt_text(password) if password else None,
            security_type=security_type or None,
            vlan_id=vlan_id,
            notes=notes.strip() if notes else None,
        )

        db.add(ssid)
        db.commit()
        db.refresh(ssid)

        return ssid

    @staticmethod
    def update_ssid(
        db: Session,
        *,
        ssid: SSID,
        name: str,
        password: str | None = None,
        update_password: bool = False,
        security_type: str | None = None,
        vlan_id: int | None = None,
        notes: str | None = None,
    ) -> SSID:
        name = name.strip()

        if not name:
            raise ValueError("SSID name is required.")

        security_type = security_type or ""

        if security_type not in VALID_SECURITY_TYPES:
            raise ValueError("Invalid security type.")

        existing = db.scalar(
            select(SSID).where(
                SSID.location_id == ssid.location_id,
                func.lower(SSID.name) == name.lower(),
                SSID.id != ssid.id,
                SSID.is_deleted.is_(False),
            )
        )

        if existing:
            raise ValueError("An SSID with this name already exists in this location.")

        if vlan_id is not None:
            vlan = db.get(VLAN, vlan_id)

            if vlan is None or vlan.is_deleted:
                raise ValueError("Selected VLAN does not exist.")

            if vlan.location_id != ssid.location_id:
                raise ValueError("Selected VLAN does not belong to this location.")

        ssid.name = name
        ssid.security_type = security_type or None
        ssid.vlan_id = vlan_id
        ssid.notes = notes.strip() if notes else None

        if update_password:
            ssid.encrypted_password = encrypt_text(password) if password else None

        db.add(ssid)
        db.commit()
        db.refresh(ssid)

        return ssid

    @staticmethod
    def reveal_password(
        ssid: SSID,
    ) -> str | None:
        return decrypt_text(ssid.encrypted_password)

    @staticmethod
    def get_delete_blockers(
        db: Session,
        ssid: SSID,
    ) -> list[str]:
        ap_count = db.scalar(
            select(func.count(SSIDAccessPoint.id)).where(
                SSIDAccessPoint.ssid_id == ssid.id,
            )
        )

        blockers: list[str] = []

        if ap_count:
            blockers.append(f"{ap_count} access point assignment(s)")

        return blockers

    @staticmethod
    def delete_ssid(
        db: Session,
        ssid: SSID,
    ) -> None:
        blockers = SSIDService.get_delete_blockers(
            db,
            ssid,
        )

        if blockers:
            raise ValueError(
                "Cannot delete SSID. Please remove: "
                + ", ".join(blockers)
                + "."
            )

        ssid.is_deleted = True

        db.add(ssid)
        db.commit()