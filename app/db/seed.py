from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.device_type import DeviceType


DEFAULT_DEVICE_TYPES = [
    {
        "name": "Router",
        "slug": "router",
        "description": "Network router",
        "icon_path": "/static/icons/router.svg",
    },
    {
        "name": "Switch",
        "slug": "switch",
        "description": "Network switch",
        "icon_path": "/static/icons/switch.svg",
    },
    {
        "name": "Access Point",
        "slug": "access-point",
        "description": "Wireless access point",
        "icon_path": "/static/icons/access-point.svg",
    },
    {
        "name": "Server",
        "slug": "server",
        "description": "Physical or virtual server",
        "icon_path": "/static/icons/server.svg",
    },
    {
        "name": "Workstation",
        "slug": "workstation",
        "description": "Desktop or laptop computer",
        "icon_path": "/static/icons/workstation.svg",
    },
    {
        "name": "Printer",
        "slug": "printer",
        "description": "Network printer",
        "icon_path": "/static/icons/printer.svg",
    },
    {
        "name": "Camera",
        "slug": "camera",
        "description": "IP security camera",
        "icon_path": "/static/icons/camera.svg",
    },
    {
        "name": "NVR",
        "slug": "nvr",
        "description": "Network video recorder",
        "icon_path": "/static/icons/nvr.svg",
    },
    {
        "name": "NAS",
        "slug": "nas",
        "description": "Network attached storage",
        "icon_path": "/static/icons/nas.svg",
    },
    {
        "name": "UPS",
        "slug": "ups",
        "description": "Uninterruptible power supply",
        "icon_path": "/static/icons/ups.svg",
    },
]


def seed_device_types() -> None:
    with SessionLocal() as db:
        for device_type_data in DEFAULT_DEVICE_TYPES:
            existing = db.scalar(
                select(DeviceType).where(
                    DeviceType.slug == device_type_data["slug"]
                )
            )

            if existing:
                continue

            db.add(
                DeviceType(
                    name=device_type_data["name"],
                    slug=device_type_data["slug"],
                    description=device_type_data["description"],
                    icon_path=device_type_data["icon_path"],
                    is_default=True,
                    is_active=True,
                )
            )

        db.commit()


def run_seeds() -> None:
    print("Seeding device types...")
    seed_device_types()
    print("Done.")


if __name__ == "__main__":
    run_seeds()