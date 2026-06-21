from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db, require_admin
from app.models.user import User
from app.services.audit_service import AuditService
from app.services.location_service import LocationService
from app.services.ssid_access_point_service import SSIDAccessPointService
from app.services.ssid_service import SSIDService
from app.web.context import build_template_context


router = APIRouter(
    prefix="/ssids",
    tags=["ssids"],
)

templates = Jinja2Templates(
    directory="app/web/templates",
)


@router.get("", response_class=HTMLResponse)
async def list_ssids(
    request: Request,
    error: str = Query(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_location = None

    if current_user.selected_location_id:
        current_location = LocationService.get_location(
            db,
            current_user.selected_location_id,
        )

    ssids = SSIDService.list_ssids(
        db,
        location_id=current_location.id if current_location else None,
    )

    return templates.TemplateResponse(
        request=request,
        name="ssids/list.html",
        context=build_template_context(
            title="SSIDs",
            current_user=current_user,
            db=db,
            current_location=current_location,
            ssids=ssids,
            error=error,
        ),
    )


@router.get("/create", response_class=HTMLResponse)
async def create_ssid_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    current_location = None

    if current_user.selected_location_id:
        current_location = LocationService.get_location(
            db,
            current_user.selected_location_id,
        )

    return templates.TemplateResponse(
        request=request,
        name="ssids/create.html",
        context=build_template_context(
            title="Create SSID",
            current_user=current_user,
            db=db,
            current_location=current_location,
            vlans=SSIDService.list_vlans_for_location(db, current_location.id)
            if current_location
            else [],
            error=None,
        ),
    )


@router.post("/create")
async def create_ssid_submit(
    request: Request,
    name: str = Form(...),
    password: str = Form(""),
    security_type: str = Form(""),
    vlan_id: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    current_location = None

    if current_user.selected_location_id:
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
        SSIDService.create_ssid(
            db,
            location_id=current_location.id,
            name=name,
            password=password,
            security_type=security_type,
            vlan_id=int(vlan_id) if vlan_id else None,
            notes=notes,
        )

        return RedirectResponse(
            url="/ssids",
            status_code=303,
        )

    except ValueError as exc:
        return templates.TemplateResponse(
            request=request,
            name="ssids/create.html",
            context=build_template_context(
                title="Create SSID",
                current_user=current_user,
                db=db,
                current_location=current_location,
                vlans=SSIDService.list_vlans_for_location(db, current_location.id),
                error=str(exc),
                form_data={
                    "name": name,
                    "security_type": security_type,
                    "vlan_id": vlan_id,
                    "notes": notes,
                },
            ),
            status_code=400,
        )


@router.get("/{ssid_id}", response_class=HTMLResponse)
async def ssid_detail(
    ssid_id: int,
    request: Request,
    error: str = Query(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ssid = SSIDService.get_ssid(db, ssid_id)

    if ssid is None:
        return RedirectResponse(url="/ssids", status_code=303)

    assignments = SSIDAccessPointService.list_assignments(db, ssid.id)

    return templates.TemplateResponse(
        request=request,
        name="ssids/detail.html",
        context=build_template_context(
            title=ssid.name,
            current_user=current_user,
            db=db,
            current_location=LocationService.get_location(db, ssid.location_id),
            ssid=ssid,
            assignments=assignments,
            error=error,
        ),
    )


@router.get("/{ssid_id}/reveal-password", response_class=HTMLResponse)
async def reveal_ssid_password_confirm(
    ssid_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    ssid = SSIDService.get_ssid(db, ssid_id)

    if ssid is None:
        return RedirectResponse(url="/ssids", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="ssids/reveal_password.html",
        context=build_template_context(
            title=f"Reveal Password - {ssid.name}",
            current_user=current_user,
            db=db,
            current_location=LocationService.get_location(db, ssid.location_id),
            ssid=ssid,
            revealed_password=None,
            reveal_timeout_seconds=60,
        ),
    )


@router.post("/{ssid_id}/reveal-password", response_class=HTMLResponse)
async def reveal_ssid_password_submit(
    ssid_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    ssid = SSIDService.get_ssid(db, ssid_id)

    if ssid is None:
        return RedirectResponse(url="/ssids", status_code=303)

    revealed_password = SSIDService.reveal_password(ssid)

    AuditService.log_event(
        db,
        user=current_user,
        action="SSID Password Revealed",
        entity_type="ssid",
        entity_id=ssid.id,
        details=f"Password revealed for SSID '{ssid.name}'.",
        request=request,
    )

    return templates.TemplateResponse(
        request=request,
        name="ssids/reveal_password.html",
        context=build_template_context(
            title=f"Reveal Password - {ssid.name}",
            current_user=current_user,
            db=db,
            current_location=LocationService.get_location(db, ssid.location_id),
            ssid=ssid,
            revealed_password=revealed_password,
            reveal_timeout_seconds=60,
        ),
    )


@router.get("/{ssid_id}/edit", response_class=HTMLResponse)
async def edit_ssid_form(
    ssid_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    ssid = SSIDService.get_ssid(db, ssid_id)

    if ssid is None:
        return RedirectResponse(url="/ssids", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="ssids/edit.html",
        context=build_template_context(
            title=f"Edit {ssid.name}",
            current_user=current_user,
            db=db,
            current_location=LocationService.get_location(db, ssid.location_id),
            ssid=ssid,
            vlans=SSIDService.list_vlans_for_location(db, ssid.location_id),
            error=None,
        ),
    )


@router.post("/{ssid_id}/edit")
async def edit_ssid_submit(
    ssid_id: int,
    request: Request,
    name: str = Form(...),
    password: str = Form(""),
    update_password: bool = Form(False),
    security_type: str = Form(""),
    vlan_id: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    ssid = SSIDService.get_ssid(db, ssid_id)

    if ssid is None:
        return RedirectResponse(url="/ssids", status_code=303)

    try:
        SSIDService.update_ssid(
            db,
            ssid=ssid,
            name=name,
            password=password,
            update_password=update_password,
            security_type=security_type,
            vlan_id=int(vlan_id) if vlan_id else None,
            notes=notes,
        )

        return RedirectResponse(url=f"/ssids/{ssid.id}", status_code=303)

    except ValueError as exc:
        return templates.TemplateResponse(
            request=request,
            name="ssids/edit.html",
            context=build_template_context(
                title=f"Edit {ssid.name}",
                current_user=current_user,
                db=db,
                current_location=LocationService.get_location(db, ssid.location_id),
                ssid=ssid,
                vlans=SSIDService.list_vlans_for_location(db, ssid.location_id),
                error=str(exc),
            ),
            status_code=400,
        )


@router.get("/{ssid_id}/access-points", response_class=HTMLResponse)
async def manage_ssid_access_points(
    ssid_id: int,
    request: Request,
    error: str = Query(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    ssid = SSIDService.get_ssid(db, ssid_id)

    if ssid is None:
        return RedirectResponse(url="/ssids", status_code=303)

    assignments = SSIDAccessPointService.list_assignments(db, ssid.id)

    available_devices = SSIDAccessPointService.list_available_access_points(
        db,
        location_id=ssid.location_id,
        ssid_id=ssid.id,
    )

    return templates.TemplateResponse(
        request=request,
        name="ssids/access_points.html",
        context=build_template_context(
            title=f"Access Points - {ssid.name}",
            current_user=current_user,
            db=db,
            current_location=LocationService.get_location(db, ssid.location_id),
            ssid=ssid,
            assignments=assignments,
            available_devices=available_devices,
            error=error,
        ),
    )


@router.post("/{ssid_id}/access-points/add")
async def add_ssid_access_point(
    ssid_id: int,
    device_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    ssid = SSIDService.get_ssid(db, ssid_id)

    if ssid is None:
        return RedirectResponse(url="/ssids", status_code=303)

    try:
        SSIDAccessPointService.add_assignment(
            db,
            ssid=ssid,
            device_id=device_id,
        )

    except ValueError as exc:
        query_string = urlencode({"error": str(exc)})

        return RedirectResponse(
            url=f"/ssids/{ssid.id}/access-points?{query_string}",
            status_code=303,
        )

    return RedirectResponse(
        url=f"/ssids/{ssid.id}/access-points",
        status_code=303,
    )


@router.post("/{ssid_id}/access-points/{assignment_id}/delete")
async def delete_ssid_access_point(
    ssid_id: int,
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    ssid = SSIDService.get_ssid(db, ssid_id)

    if ssid is None:
        return RedirectResponse(url="/ssids", status_code=303)

    try:
        SSIDAccessPointService.remove_assignment(
            db,
            ssid=ssid,
            assignment_id=assignment_id,
        )

    except ValueError as exc:
        query_string = urlencode({"error": str(exc)})

        return RedirectResponse(
            url=f"/ssids/{ssid.id}/access-points?{query_string}",
            status_code=303,
        )

    return RedirectResponse(
        url=f"/ssids/{ssid.id}/access-points",
        status_code=303,
    )


@router.post("/{ssid_id}/delete")
async def delete_ssid(
    ssid_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    ssid = SSIDService.get_ssid(db, ssid_id)

    if ssid is None:
        return RedirectResponse(url="/ssids", status_code=303)

    try:
        SSIDService.delete_ssid(db, ssid)

    except ValueError as exc:
        query_string = urlencode({"error": str(exc)})

        return RedirectResponse(
            url=f"/ssids/{ssid.id}?{query_string}",
            status_code=303,
        )

    return RedirectResponse(url="/ssids", status_code=303)