from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db, require_admin
from app.models.user import User
from app.services.location_service import LocationService
from app.services.vlan_service import VLANService
from app.web.context import build_template_context


router = APIRouter(
    prefix="/vlans",
    tags=["vlans"],
)

templates = Jinja2Templates(
    directory="app/web/templates",
)


@router.get("", response_class=HTMLResponse)
async def list_vlans(
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

    vlans = VLANService.list_vlans(
        db,
        location_id=current_location.id if current_location else None,
    )

    return templates.TemplateResponse(
        request=request,
        name="vlans/list.html",
        context=build_template_context(
            title="VLANs",
            current_user=current_user,
            db=db,
            current_location=current_location,
            vlans=vlans,
            error=error,
        ),
    )


@router.get("/create", response_class=HTMLResponse)
async def create_vlan_form(
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
        name="vlans/create.html",
        context=build_template_context(
            title="Create VLAN",
            current_user=current_user,
            db=db,
            current_location=current_location,
            error=None,
        ),
    )


@router.post("/create")
async def create_vlan_submit(
    request: Request,
    name: str = Form(...),
    vlan_number: int = Form(...),
    purpose: str = Form(""),
    subnet: str = Form(""),
    gateway: str = Form(""),
    dhcp_range_start: str = Form(""),
    dhcp_range_end: str = Form(""),
    dns_settings: str = Form(""),
    firewall_notes: str = Form(""),
    allowed_access_rules: str = Form(""),
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

    try:
        VLANService.create_vlan(
            db,
            location_id=current_location.id,
            name=name,
            vlan_number=vlan_number,
            purpose=purpose,
            subnet=subnet,
            gateway=gateway,
            dhcp_range_start=dhcp_range_start,
            dhcp_range_end=dhcp_range_end,
            dns_settings=dns_settings,
            firewall_notes=firewall_notes,
            allowed_access_rules=allowed_access_rules,
        )

        return RedirectResponse(
            url="/vlans",
            status_code=303,
        )

    except ValueError as exc:
        return templates.TemplateResponse(
            request=request,
            name="vlans/create.html",
            context=build_template_context(
                title="Create VLAN",
                current_user=current_user,
                db=db,
                current_location=current_location,
                error=str(exc),
                form_data={
                    "name": name,
                    "vlan_number": vlan_number,
                    "purpose": purpose,
                    "subnet": subnet,
                    "gateway": gateway,
                    "dhcp_range_start": dhcp_range_start,
                    "dhcp_range_end": dhcp_range_end,
                    "dns_settings": dns_settings,
                    "firewall_notes": firewall_notes,
                    "allowed_access_rules": allowed_access_rules,
                },
            ),
            status_code=400,
        )


@router.get("/{vlan_id}", response_class=HTMLResponse)
async def detail_vlan(
    vlan_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vlan = VLANService.get_vlan(
        db,
        vlan_id,
    )

    if vlan is None:
        return RedirectResponse(
            url="/vlans",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="vlans/detail.html",
        context=build_template_context(
            title=f"VLAN {vlan.vlan_number}",
            current_user=current_user,
            db=db,
            current_location=LocationService.get_location(db, vlan.location_id),
            vlan=vlan,
        ),
    )


@router.get("/{vlan_id}/edit", response_class=HTMLResponse)
async def edit_vlan_form(
    vlan_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    vlan = VLANService.get_vlan(
        db,
        vlan_id,
    )

    if vlan is None:
        return RedirectResponse(
            url="/vlans",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="vlans/edit.html",
        context=build_template_context(
            title=f"Edit VLAN {vlan.vlan_number}",
            current_user=current_user,
            db=db,
            current_location=LocationService.get_location(db, vlan.location_id),
            vlan=vlan,
            error=None,
        ),
    )


@router.post("/{vlan_id}/edit")
async def edit_vlan_submit(
    vlan_id: int,
    request: Request,
    name: str = Form(...),
    vlan_number: int = Form(...),
    purpose: str = Form(""),
    subnet: str = Form(""),
    gateway: str = Form(""),
    dhcp_range_start: str = Form(""),
    dhcp_range_end: str = Form(""),
    dns_settings: str = Form(""),
    firewall_notes: str = Form(""),
    allowed_access_rules: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    vlan = VLANService.get_vlan(
        db,
        vlan_id,
    )

    if vlan is None:
        return RedirectResponse(
            url="/vlans",
            status_code=303,
        )

    try:
        VLANService.update_vlan(
            db,
            vlan=vlan,
            name=name,
            vlan_number=vlan_number,
            purpose=purpose,
            subnet=subnet,
            gateway=gateway,
            dhcp_range_start=dhcp_range_start,
            dhcp_range_end=dhcp_range_end,
            dns_settings=dns_settings,
            firewall_notes=firewall_notes,
            allowed_access_rules=allowed_access_rules,
        )

        return RedirectResponse(
            url="/vlans",
            status_code=303,
        )

    except ValueError as exc:
        return templates.TemplateResponse(
            request=request,
            name="vlans/edit.html",
            context=build_template_context(
                title=f"Edit VLAN {vlan.vlan_number}",
                current_user=current_user,
                db=db,
                current_location=LocationService.get_location(db, vlan.location_id),
                vlan=vlan,
                error=str(exc),
                form_data={
                    "name": name,
                    "vlan_number": vlan_number,
                    "purpose": purpose,
                    "subnet": subnet,
                    "gateway": gateway,
                    "dhcp_range_start": dhcp_range_start,
                    "dhcp_range_end": dhcp_range_end,
                    "dns_settings": dns_settings,
                    "firewall_notes": firewall_notes,
                    "allowed_access_rules": allowed_access_rules,
                },
            ),
            status_code=400,
        )


@router.post("/{vlan_id}/delete")
async def delete_vlan(
    vlan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    vlan = VLANService.get_vlan(
        db,
        vlan_id,
    )

    if vlan is None:
        return RedirectResponse(
            url="/vlans",
            status_code=303,
        )

    try:
        VLANService.delete_vlan(
            db,
            vlan,
        )

    except ValueError as exc:
        query_string = urlencode(
            {
                "error": str(exc),
            }
        )

        return RedirectResponse(
            url=f"/vlans?{query_string}",
            status_code=303,
        )

    return RedirectResponse(
        url="/vlans",
        status_code=303,
    )