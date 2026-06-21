from datetime import date
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.dependencies import get_current_user, get_db, require_admin
from app.models.ssid import SSID
from app.models.ssid_access_point import SSIDAccessPoint
from app.models.user import User
from app.services.cable_service import CableService
from app.services.device_service import DeviceService
from app.services.location_service import LocationService
from app.web.context import build_template_context


router = APIRouter(
    prefix="/devices",
    tags=["devices"],
)

templates = Jinja2Templates(
    directory="app/web/templates",
)


@router.get("", response_class=HTMLResponse)
async def list_devices(
    request: Request,
    error: str = Query(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_location = None

    if current_user.selected_location_id is not None:
        current_location = LocationService.get_location(
            db,
            current_user.selected_location_id,
        )

    devices = DeviceService.list_devices(
        db,
        location_id=current_location.id if current_location else None,
    )

    return templates.TemplateResponse(
        request=request,
        name="devices/list.html",
        context=build_template_context(
            title="Devices",
            current_user=current_user,
            db=db,
            current_location=current_location,
            devices=devices,
            error=error,
        ),
    )


@router.get("/create", response_class=HTMLResponse)
async def create_device_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    current_location = None

    if current_user.selected_location_id is not None:
        current_location = LocationService.get_location(
            db,
            current_user.selected_location_id,
        )

    return templates.TemplateResponse(
        request=request,
        name="devices/create.html",
        context=build_template_context(
            title="Create Device",
            current_user=current_user,
            db=db,
            current_location=current_location,
            device_types=DeviceService.list_device_types(db),
            vlans=DeviceService.list_vlans_for_location(db, current_location.id)
            if current_location
            else [],
            error=None,
        ),
    )


@router.post("/create")
async def create_device_submit(
    request: Request,
    name: str = Form(...),
    device_type_id: int = Form(...),
    manufacturer: str = Form(""),
    model: str = Form(""),
    serial_number: str = Form(""),
    mac_address: str = Form(""),
    ip_assignment_type: str = Form(""),
    ip_address: str = Form(""),
    vlan_id: str = Form(""),
    power_source: str = Form("external_power"),
    supplied_by: str = Form(""),
    purchase_date_raw: str = Form("", alias="purchase_date"),
    notes: str = Form(""),
    status: str = Form("active"),
    port_count: int = Form(0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    current_location = None

    if current_user.selected_location_id is not None:
        current_location = LocationService.get_location(
            db,
            current_user.selected_location_id,
        )

    if current_location is None:
        return RedirectResponse(
            url="/admin/locations",
            status_code=303,
        )

    parsed_purchase_date: date | None = None

    if purchase_date_raw:
        parsed_purchase_date = date.fromisoformat(purchase_date_raw)

    parsed_vlan_id = int(vlan_id) if vlan_id else None

    try:
        DeviceService.create_device(
            db,
            name=name,
            location_id=current_location.id,
            device_type_id=device_type_id,
            manufacturer=manufacturer,
            model=model,
            serial_number=serial_number,
            mac_address=mac_address,
            ip_assignment_type=ip_assignment_type,
            ip_address=ip_address,
            vlan_id=parsed_vlan_id,
            power_source=power_source,
            supplied_by=supplied_by,
            purchase_date=parsed_purchase_date,
            notes=notes,
            status=status,
            port_count=port_count,
        )

        return RedirectResponse(
            url="/devices",
            status_code=303,
        )

    except ValueError as exc:
        return templates.TemplateResponse(
            request=request,
            name="devices/create.html",
            context=build_template_context(
                title="Create Device",
                current_user=current_user,
                db=db,
                current_location=current_location,
                device_types=DeviceService.list_device_types(db),
                vlans=DeviceService.list_vlans_for_location(db, current_location.id),
                error=str(exc),
                form_data={
                    "name": name,
                    "device_type_id": device_type_id,
                    "manufacturer": manufacturer,
                    "model": model,
                    "serial_number": serial_number,
                    "mac_address": mac_address,
                    "ip_assignment_type": ip_assignment_type,
                    "ip_address": ip_address,
                    "vlan_id": vlan_id,
                    "power_source": power_source,
                    "supplied_by": supplied_by,
                    "purchase_date": purchase_date_raw,
                    "notes": notes,
                    "status": status,
                    "port_count": port_count,
                },
            ),
            status_code=400,
        )


@router.get("/{device_id}", response_class=HTMLResponse)
async def detail_device(
    device_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    device = DeviceService.get_device_with_ports(db, device_id)

    if device is None:
        return RedirectResponse(
            url="/devices",
            status_code=303,
        )

    port_cable_map = CableService.get_device_cable_map(
        db,
        device.id,
    )

    ssid_assignments = list(
        db.scalars(
            select(SSIDAccessPoint)
            .options(
                selectinload(SSIDAccessPoint.ssid).selectinload(SSID.vlan),
            )
            .where(
                SSIDAccessPoint.device_id == device.id,
            )
            .order_by(
                SSIDAccessPoint.id.asc(),
            )
        )
    )

    return templates.TemplateResponse(
        request=request,
        name="devices/detail.html",
        context=build_template_context(
            title=device.name,
            current_user=current_user,
            db=db,
            current_location=LocationService.get_location(db, device.location_id),
            device=device,
            ports=device.ports,
            port_cable_map=port_cable_map,
            ssid_assignments=ssid_assignments,
        ),
    )


@router.get("/{device_id}/edit", response_class=HTMLResponse)
async def edit_device_form(
    device_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    device = DeviceService.get_device(db, device_id)

    if device is None:
        return RedirectResponse(
            url="/devices",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="devices/edit.html",
        context=build_template_context(
            title="Edit Device",
            current_user=current_user,
            db=db,
            current_location=LocationService.get_location(db, device.location_id),
            device=device,
            device_types=DeviceService.list_device_types(db),
            vlans=DeviceService.list_vlans_for_location(db, device.location_id),
            error=None,
        ),
    )


@router.post("/{device_id}/edit")
async def edit_device_submit(
    device_id: int,
    request: Request,
    name: str = Form(...),
    device_type_id: int = Form(...),
    manufacturer: str = Form(""),
    model: str = Form(""),
    serial_number: str = Form(""),
    mac_address: str = Form(""),
    ip_assignment_type: str = Form(""),
    ip_address: str = Form(""),
    vlan_id: str = Form(""),
    power_source: str = Form("external_power"),
    supplied_by: str = Form(""),
    purchase_date_raw: str = Form("", alias="purchase_date"),
    notes: str = Form(""),
    status: str = Form("active"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    device = DeviceService.get_device(db, device_id)

    if device is None:
        return RedirectResponse(
            url="/devices",
            status_code=303,
        )

    parsed_purchase_date: date | None = None

    if purchase_date_raw:
        parsed_purchase_date = date.fromisoformat(purchase_date_raw)

    parsed_vlan_id = int(vlan_id) if vlan_id else None

    try:
        DeviceService.update_device(
            db,
            device=device,
            name=name,
            location_id=device.location_id,
            device_type_id=device_type_id,
            manufacturer=manufacturer,
            model=model,
            serial_number=serial_number,
            mac_address=mac_address,
            ip_assignment_type=ip_assignment_type,
            ip_address=ip_address,
            vlan_id=parsed_vlan_id,
            power_source=power_source,
            supplied_by=supplied_by,
            purchase_date=parsed_purchase_date,
            notes=notes,
            status=status,
        )

        return RedirectResponse(
            url="/devices",
            status_code=303,
        )

    except ValueError as exc:
        return templates.TemplateResponse(
            request=request,
            name="devices/edit.html",
            context=build_template_context(
                title="Edit Device",
                current_user=current_user,
                db=db,
                current_location=LocationService.get_location(db, device.location_id),
                device=device,
                device_types=DeviceService.list_device_types(db),
                vlans=DeviceService.list_vlans_for_location(db, device.location_id),
                error=str(exc),
            ),
            status_code=400,
        )


@router.post("/{device_id}/delete")
async def delete_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    device = DeviceService.get_device(db, device_id)

    if device is None:
        return RedirectResponse(
            url="/devices",
            status_code=303,
        )

    try:
        DeviceService.delete_device(db, device)

    except ValueError as exc:
        query_string = urlencode(
            {
                "error": str(exc),
            }
        )

        return RedirectResponse(
            url=f"/devices?{query_string}",
            status_code=303,
        )

    return RedirectResponse(
        url="/devices",
        status_code=303,
    )