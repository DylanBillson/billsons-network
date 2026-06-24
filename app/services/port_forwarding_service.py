from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.device import Device
from app.models.device_type import DeviceType
from app.models.port_forwarding_rule import PortForwardingRule


VALID_PROTOCOLS = {
    "tcp",
    "udp",
    "tcp_udp",
}


class PortForwardingService:
    @staticmethod
    def list_rules_for_router(
        db: Session,
        router_device_id: int,
    ) -> list[PortForwardingRule]:
        return list(
            db.scalars(
                select(PortForwardingRule)
                .where(
                    PortForwardingRule.router_device_id == router_device_id,
                    PortForwardingRule.is_deleted.is_(False),
                )
                .order_by(
                    PortForwardingRule.is_enabled.desc(),
                    PortForwardingRule.external_port_start.asc(),
                    PortForwardingRule.rule_name.asc(),
                )
            )
        )

    @staticmethod
    def get_rule(
        db: Session,
        rule_id: int,
    ) -> PortForwardingRule | None:
        return db.scalar(
            select(PortForwardingRule)
            .options(
                selectinload(PortForwardingRule.router_device)
                .selectinload(Device.device_type),
            )
            .where(
                PortForwardingRule.id == rule_id,
                PortForwardingRule.is_deleted.is_(False),
            )
        )

    @staticmethod
    def is_router_device(
        device: Device,
    ) -> bool:
        if device.device_type is None:
            return False

        return device.device_type.slug == "router"

    @staticmethod
    def get_router_device(
        db: Session,
        router_device_id: int,
    ) -> Device | None:
        return db.scalar(
            select(Device)
            .options(
                selectinload(Device.device_type),
            )
            .where(
                Device.id == router_device_id,
                Device.is_deleted.is_(False),
            )
        )

    @staticmethod
    def list_router_devices_for_location(
        db: Session,
        location_id: int,
    ) -> list[Device]:
        return list(
            db.scalars(
                select(Device)
                .join(DeviceType, Device.device_type_id == DeviceType.id)
                .where(
                    Device.location_id == location_id,
                    Device.is_deleted.is_(False),
                    DeviceType.slug == "router",
                    DeviceType.is_active.is_(True),
                )
                .order_by(
                    Device.name.asc(),
                )
            )
        )

    @staticmethod
    def _validate_protocol(
        protocol: str,
    ) -> str:
        protocol = protocol.strip().lower()

        if protocol not in VALID_PROTOCOLS:
            raise ValueError(
                "Protocol must be TCP, UDP, or TCP/UDP."
            )

        return protocol

    @staticmethod
    def _validate_port(
        value: int,
        field_name: str,
    ) -> int:
        if value < 1 or value > 65535:
            raise ValueError(
                f"{field_name} must be between 1 and 65535."
            )

        return value

    @staticmethod
    def _normalise_optional_port_end(
        start: int,
        end: int | None,
        field_name: str,
    ) -> int | None:
        if end is None:
            return None

        if end < 1 or end > 65535:
            raise ValueError(
                f"{field_name} must be between 1 and 65535."
            )

        if end < start:
            raise ValueError(
                f"{field_name} cannot be lower than the start port."
            )

        if end == start:
            return None

        return end

    @staticmethod
    def create_rule(
        db: Session,
        *,
        router_device_id: int,
        rule_name: str,
        external_port_start: int,
        external_port_end: int | None,
        internal_ip_address: str,
        internal_port_start: int,
        internal_port_end: int | None,
        protocol: str,
        is_enabled: bool,
        notes: str,
    ) -> PortForwardingRule:
        router_device = PortForwardingService.get_router_device(
            db,
            router_device_id,
        )

        if router_device is None:
            raise ValueError(
                "Router device not found."
            )

        if not PortForwardingService.is_router_device(router_device):
            raise ValueError(
                "Port forwarding rules can only be added to router devices."
            )

        rule_name = rule_name.strip()
        internal_ip_address = internal_ip_address.strip()
        protocol = PortForwardingService._validate_protocol(protocol)

        if not rule_name:
            raise ValueError(
                "Rule name is required."
            )

        if not internal_ip_address:
            raise ValueError(
                "Internal IP address is required."
            )

        external_port_start = PortForwardingService._validate_port(
            external_port_start,
            "External start port",
        )

        internal_port_start = PortForwardingService._validate_port(
            internal_port_start,
            "Internal start port",
        )

        external_port_end = PortForwardingService._normalise_optional_port_end(
            external_port_start,
            external_port_end,
            "External end port",
        )

        internal_port_end = PortForwardingService._normalise_optional_port_end(
            internal_port_start,
            internal_port_end,
            "Internal end port",
        )

        rule = PortForwardingRule(
            router_device_id=router_device.id,
            rule_name=rule_name,
            external_port_start=external_port_start,
            external_port_end=external_port_end,
            internal_ip_address=internal_ip_address,
            internal_port_start=internal_port_start,
            internal_port_end=internal_port_end,
            protocol=protocol,
            is_enabled=is_enabled,
            notes=notes or None,
        )

        db.add(rule)
        db.commit()
        db.refresh(rule)

        return rule

    @staticmethod
    def update_rule(
        db: Session,
        *,
        rule: PortForwardingRule,
        rule_name: str,
        external_port_start: int,
        external_port_end: int | None,
        internal_ip_address: str,
        internal_port_start: int,
        internal_port_end: int | None,
        protocol: str,
        is_enabled: bool,
        notes: str,
    ) -> PortForwardingRule:
        router_device = PortForwardingService.get_router_device(
            db,
            rule.router_device_id,
        )

        if router_device is None:
            raise ValueError(
                "Router device not found."
            )

        if not PortForwardingService.is_router_device(router_device):
            raise ValueError(
                "Port forwarding rules can only belong to router devices."
            )

        rule_name = rule_name.strip()
        internal_ip_address = internal_ip_address.strip()
        protocol = PortForwardingService._validate_protocol(protocol)

        if not rule_name:
            raise ValueError(
                "Rule name is required."
            )

        if not internal_ip_address:
            raise ValueError(
                "Internal IP address is required."
            )

        external_port_start = PortForwardingService._validate_port(
            external_port_start,
            "External start port",
        )

        internal_port_start = PortForwardingService._validate_port(
            internal_port_start,
            "Internal start port",
        )

        external_port_end = PortForwardingService._normalise_optional_port_end(
            external_port_start,
            external_port_end,
            "External end port",
        )

        internal_port_end = PortForwardingService._normalise_optional_port_end(
            internal_port_start,
            internal_port_end,
            "Internal end port",
        )

        rule.rule_name = rule_name
        rule.external_port_start = external_port_start
        rule.external_port_end = external_port_end
        rule.internal_ip_address = internal_ip_address
        rule.internal_port_start = internal_port_start
        rule.internal_port_end = internal_port_end
        rule.protocol = protocol
        rule.is_enabled = is_enabled
        rule.notes = notes or None

        db.add(rule)
        db.commit()
        db.refresh(rule)

        return rule

    @staticmethod
    def delete_rule(
        db: Session,
        rule: PortForwardingRule,
    ) -> None:
        db.delete(rule)
        db.commit()