from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.device import Device
from app.models.device_type import DeviceType
from app.models.ssid import SSID
from app.models.ssid_access_point import SSIDAccessPoint


class SSIDAccessPointService:
    @staticmethod
    def list_assignments(
        db: Session,
        ssid_id: int,
    ) -> list[SSIDAccessPoint]:
        return list(
            db.scalars(
                select(SSIDAccessPoint)
                .options(
                    selectinload(SSIDAccessPoint.device)
                    .selectinload(Device.device_type),
                )
                .where(
                    SSIDAccessPoint.ssid_id == ssid_id,
                )
                .order_by(
                    SSIDAccessPoint.id.asc(),
                )
            )
        )

    @staticmethod
    def list_available_access_points(
        db: Session,
        *,
        location_id: int,
        ssid_id: int,
    ) -> list[Device]:
        assigned_device_ids = select(SSIDAccessPoint.device_id).where(
            SSIDAccessPoint.ssid_id == ssid_id,
        )

        return list(
            db.scalars(
                select(Device)
                .join(DeviceType, DeviceType.id == Device.device_type_id)
                .where(
                    Device.location_id == location_id,
                    Device.is_deleted.is_(False),
                    func.lower(DeviceType.name).in_(
                        [
                            "access point",
                            "ap",
                        ]
                    ),
                    Device.id.not_in(assigned_device_ids),
                )
                .order_by(Device.name.asc())
            )
        )

    @staticmethod
    def add_assignment(
        db: Session,
        *,
        ssid: SSID,
        device_id: int,
    ) -> SSIDAccessPoint:
        device = db.get(Device, device_id)

        if device is None or device.is_deleted:
            raise ValueError("Selected access point does not exist.")

        if device.location_id != ssid.location_id:
            raise ValueError("Selected access point does not belong to this location.")

        if device.device_type is None:
            raise ValueError("Selected device does not have a device type.")

        if device.device_type.name.lower() not in {
            "access point",
            "ap",
        }:
            raise ValueError("Selected device is not an access point.")

        existing = db.scalar(
            select(SSIDAccessPoint).where(
                SSIDAccessPoint.ssid_id == ssid.id,
                SSIDAccessPoint.device_id == device_id,
            )
        )

        if existing:
            raise ValueError("This access point is already assigned to this SSID.")

        assignment = SSIDAccessPoint(
            ssid_id=ssid.id,
            device_id=device_id,
        )

        db.add(assignment)
        db.commit()
        db.refresh(assignment)

        return assignment

    @staticmethod
    def remove_assignment(
        db: Session,
        *,
        ssid: SSID,
        assignment_id: int,
    ) -> None:
        assignment = db.get(
            SSIDAccessPoint,
            assignment_id,
        )

        if assignment is None or assignment.ssid_id != ssid.id:
            raise ValueError("Access point assignment does not exist.")

        db.delete(assignment)
        db.commit()