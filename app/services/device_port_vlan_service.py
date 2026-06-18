from sqlalchemy.orm import Session

from app.models.device import Device
from app.models.device_port import DevicePort
from app.models.vlan import VLAN


VALID_PORT_VLAN_MODES = {
    "none",
    "access",
    "trunk",
    "uplink",
}


class DevicePortVLANService:
    @staticmethod
    def update_port_vlan(
        db: Session,
        *,
        port: DevicePort,
        vlan_mode: str,
        vlan_id: int | None = None,
        vlan_notes: str | None = None,
    ) -> DevicePort:
        if vlan_mode not in VALID_PORT_VLAN_MODES:
            raise ValueError("Invalid VLAN mode.")

        if vlan_mode == "none":
            vlan_id = None

        if vlan_id is not None:
            vlan = db.get(VLAN, vlan_id)

            if vlan is None or vlan.is_deleted:
                raise ValueError("Selected VLAN does not exist.")

            device = db.get(Device, port.device_id)

            if device is None or device.is_deleted:
                raise ValueError("Port device does not exist.")

            if vlan.location_id != device.location_id:
                raise ValueError("Selected VLAN does not belong to this device location.")

        port.vlan_mode = vlan_mode
        port.vlan_id = vlan_id
        port.vlan_notes = vlan_notes.strip() if vlan_notes else None

        db.add(port)
        db.commit()
        db.refresh(port)

        return port