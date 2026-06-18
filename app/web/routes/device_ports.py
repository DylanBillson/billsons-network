from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_admin
from app.models.user import User
from app.services.cable_service import CableService
from app.services.device_port_service import DevicePortService
from app.services.device_port_vlan_service import DevicePortVLANService
from app.services.device_service import DeviceService
from app.services.location_service import LocationService
from app.web.context import build_template_context


router = APIRouter(
    prefix="/devices",
    tags=["device-ports"],
)

templates = Jinja2Templates(
    directory="app/web/templates",
)


def _parse_optional_int(value: str) -> int | None:
    if not value:
        return None

    return int(value)


@router.get("/{device_id}/ports", response_class=HTMLResponse)
async def list_device_ports(
    device_id: int,
    request: Request,
    error: str = Query(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    device = DeviceService.get_device_with_ports(
        db,
        device_id,
    )

    if device is None:
        return RedirectResponse(
            url="/devices",
            status_code=303,
        )

    ports = DevicePortService.list_ports_for_device(
        db,
        device.id,
    )

    port_cable_map = CableService.get_device_cable_map(
        db,
        device.id,
    )

    return templates.TemplateResponse(
        request=request,
        name="device_ports/list.html",
        context=build_template_context(
            title=f"Manage Ports - {device.name}",
            current_user=current_user,
            db=db,
            current_location=LocationService.get_location(db, device.location_id),
            device=device,
            ports=ports,
            port_cable_map=port_cable_map,
            error=error,
        ),
    )


@router.post("/{device_id}/ports/add")
async def add_device_ports(
    device_id: int,
    number_to_add: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    device = DeviceService.get_device(
        db,
        device_id,
    )

    if device is None:
        return RedirectResponse(
            url="/devices",
            status_code=303,
        )

    try:
        DevicePortService.add_ports(
            db,
            device=device,
            number_to_add=number_to_add,
        )

    except ValueError as exc:
        query_string = urlencode(
            {
                "error": str(exc),
            }
        )

        return RedirectResponse(
            url=f"/devices/{device.id}/ports?{query_string}",
            status_code=303,
        )

    return RedirectResponse(
        url=f"/devices/{device.id}/ports",
        status_code=303,
    )


@router.get("/{device_id}/ports/{port_id}/edit", response_class=HTMLResponse)
async def edit_device_port_form(
    device_id: int,
    port_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    device = DeviceService.get_device(
        db,
        device_id,
    )

    port = DevicePortService.get_port(
        db,
        port_id,
    )

    if device is None or port is None or port.device_id != device.id:
        return RedirectResponse(
            url="/devices",
            status_code=303,
        )

    cable = CableService.get_port_cable(
        db,
        port.id,
    )

    vlans = DevicePortService.list_vlans_for_port_device(
        db,
        port,
    )

    return templates.TemplateResponse(
        request=request,
        name="device_ports/edit.html",
        context=build_template_context(
            title=f"Edit Port - {device.name}",
            current_user=current_user,
            db=db,
            current_location=LocationService.get_location(db, device.location_id),
            device=device,
            port=port,
            cable=cable,
            vlans=vlans,
            error=None,
        ),
    )


@router.post("/{device_id}/ports/{port_id}/edit")
async def edit_device_port_submit(
    device_id: int,
    port_id: int,
    label: str = Form(...),
    sort_order: int = Form(...),
    vlan_mode: str = Form("none"),
    vlan_id: str = Form(""),
    vlan_notes: str = Form(""),
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    device = DeviceService.get_device(
        db,
        device_id,
    )

    port = DevicePortService.get_port(
        db,
        port_id,
    )

    if device is None or port is None or port.device_id != device.id:
        return RedirectResponse(
            url="/devices",
            status_code=303,
        )

    try:
        DevicePortService.update_port(
            db,
            port=port,
            label=label,
            sort_order=sort_order,
        )

        DevicePortVLANService.update_port_vlan(
            db,
            port=port,
            vlan_mode=vlan_mode,
            vlan_id=_parse_optional_int(vlan_id),
            vlan_notes=vlan_notes,
        )

        return RedirectResponse(
            url=f"/devices/{device.id}/ports",
            status_code=303,
        )

    except ValueError as exc:
        cable = CableService.get_port_cable(
            db,
            port.id,
        )

        vlans = DevicePortService.list_vlans_for_port_device(
            db,
            port,
        )

        return templates.TemplateResponse(
            request=request,
            name="device_ports/edit.html",
            context=build_template_context(
                title=f"Edit Port - {device.name}",
                current_user=current_user,
                db=db,
                current_location=LocationService.get_location(db, device.location_id),
                device=device,
                port=port,
                cable=cable,
                vlans=vlans,
                error=str(exc),
                form_data={
                    "label": label,
                    "sort_order": sort_order,
                    "vlan_mode": vlan_mode,
                    "vlan_id": vlan_id,
                    "vlan_notes": vlan_notes,
                },
            ),
            status_code=400,
        )


@router.post("/{device_id}/ports/{port_id}/delete")
async def delete_device_port(
    device_id: int,
    port_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    device = DeviceService.get_device(
        db,
        device_id,
    )

    port = DevicePortService.get_port(
        db,
        port_id,
    )

    if device is None or port is None or port.device_id != device.id:
        return RedirectResponse(
            url="/devices",
            status_code=303,
        )

    cable = CableService.get_port_cable(
        db,
        port.id,
    )

    if cable is not None:
        query_string = urlencode(
            {
                "error": f"Cannot delete port {port.label}; it is connected to cable {cable.cable_id}.",
            }
        )

        return RedirectResponse(
            url=f"/devices/{device.id}/ports?{query_string}",
            status_code=303,
        )

    DevicePortService.delete_port(
        db,
        port,
    )

    return RedirectResponse(
        url=f"/devices/{device.id}/ports",
        status_code=303,
    )