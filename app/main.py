from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.web.routes import (
    admin_router,
    auth_router,
    cables_router,
    dashboard_router,
    device_ports_router,
    devices_router,
    locations_router,
    ssids_router,
    vlans_router,
)

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(locations_router)
app.include_router(devices_router)
app.include_router(device_ports_router)
app.include_router(cables_router)
app.include_router(vlans_router)
app.include_router(ssids_router)
app.include_router(admin_router)


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "application": settings.APP_NAME,
        "environment": settings.APP_ENV,
    }