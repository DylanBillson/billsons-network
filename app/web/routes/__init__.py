from app.web.routes.admin import router as admin_router
from app.web.routes.auth import router as auth_router
from app.web.routes.cables import router as cables_router
from app.web.routes.dashboard import router as dashboard_router
from app.web.routes.device_ports import router as device_ports_router
from app.web.routes.devices import router as devices_router
from app.web.routes.device_types import router as device_types_router
from app.web.routes.locations import router as locations_router
from app.web.routes.port_forwarding import router as port_forwarding_router
from app.web.routes.ssids import router as ssids_router
from app.web.routes.vlans import router as vlans_router

__all__ = [
    "admin_router",
    "auth_router",
    "cables_router",
    "dashboard_router",
    "device_ports_router",
    "devices_router",
    "device_types_router",
    "locations_router",
    "port_forwarding_router",
    "ssids_router",
    "vlans_router",
]