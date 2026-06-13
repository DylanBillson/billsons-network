from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.device import Device
from app.models.device_port import DevicePort


class DevicePortService:
    @staticmethod
    def list_ports_for_device(
        db: Session,
        device_id: int,
    ) -> list[DevicePort]:
        return list(
            db.scalars(
                select(DevicePort)
                .where(DevicePort.device_id == device_id)
                .order_by(DevicePort.sort_order.asc())
            )
        )

    @staticmethod
    def get_port(
        db: Session,
        port_id: int,
    ) -> DevicePort | None:
        return db.get(DevicePort, port_id)

    @staticmethod
    def add_ports(
        db: Session,
        *,
        device: Device,
        number_to_add: int,
    ) -> None:
        if number_to_add <= 0:
            raise ValueError("Number of ports to add must be greater than zero.")

        current_max = db.scalar(
            select(func.max(DevicePort.sort_order)).where(
                DevicePort.device_id == device.id,
            )
        ) or 0

        for offset in range(1, number_to_add + 1):
            sort_order = current_max + offset

            db.add(
                DevicePort(
                    device_id=device.id,
                    label=str(sort_order),
                    sort_order=sort_order,
                )
            )

        db.commit()

    @staticmethod
    def update_port(
        db: Session,
        *,
        port: DevicePort,
        label: str,
        sort_order: int,
    ) -> DevicePort:
        label = label.strip()

        if not label:
            raise ValueError("Port label is required.")

        if sort_order < 1:
            raise ValueError("Sort order must be at least 1.")

        existing_label = db.scalar(
            select(DevicePort).where(
                DevicePort.device_id == port.device_id,
                func.lower(DevicePort.label) == label.lower(),
                DevicePort.id != port.id,
            )
        )

        if existing_label:
            raise ValueError("Another port on this device already uses that label.")

        existing_sort_order = db.scalar(
            select(DevicePort).where(
                DevicePort.device_id == port.device_id,
                DevicePort.sort_order == sort_order,
                DevicePort.id != port.id,
            )
        )

        if existing_sort_order:
            raise ValueError("Another port on this device already uses that sort order.")

        port.label = label
        port.sort_order = sort_order

        db.add(port)
        db.commit()
        db.refresh(port)

        return port

    @staticmethod
    def delete_port(
        db: Session,
        port: DevicePort,
    ) -> None:
        # Cable dependency checks will be added when the Cables module exists.
        db.delete(port)
        db.commit()