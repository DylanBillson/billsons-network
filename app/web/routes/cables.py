from datetime import date

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db, require_admin
from app.models.user import User
from app.services.cable_service import CableService
from app.services.location_service import LocationService
from app.web.context import build_template_context


router = APIRouter(
    prefix="/cables",
    tags=["cables"],
)

templates = Jinja2Templates(
    directory="app/web/templates",
)


def _parse_date(value: str) -> date | None:
    if not value:
        return None

    return date.fromisoformat(value)


def _parse_port_id(value: str) -> int | None:
    if not value:
        return None

    return int(value)


@router.get("", response_class=HTMLResponse)
async def list_cables(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_location = None

    if current_user.selected_location_id is not None:
        current_location = LocationService.get_location(
            db,
            current_user.selected_location_id,
        )

    cables = CableService.list_cables(
        db,
        location_id=current_location.id if current_location else None,
    )

    return templates.TemplateResponse(
        request=request,
        name="cables/list.html",
        context=build_template_context(
            title="Cables",
            current_user=current_user,
            db=db,
            current_location=current_location,
            cables=cables,
        ),
    )


@router.get("/create", response_class=HTMLResponse)
async def create_cable_form(
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

    ports = (
        CableService.list_ports_for_location(db, current_location.id)
        if current_location
        else []
    )

    return templates.TemplateResponse(
        request=request,
        name="cables/create.html",
        context=build_template_context(
            title="Create Cable",
            current_user=current_user,
            db=db,
            current_location=current_location,
            ports=ports,
            error=None,
        ),
    )


@router.post("/create")
async def create_cable_submit(
    request: Request,
    cable_id: str = Form(...),
    from_port_id: str = Form(""),
    to_port_id: str = Form(""),
    cable_type: str = Form(""),
    length: str = Form(""),
    colour: str = Form(""),
    route_notes: str = Form(""),
    installed_date: str = Form(""),
    last_tested_status: str = Form(""),
    last_tested_date: str = Form(""),
    cable_supplied_by: str = Form(""),
    status: str = Form("active"),
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
        CableService.create_cable(
            db,
            cable_id=cable_id,
            location_id=current_location.id,
            from_port_id=_parse_port_id(from_port_id),
            to_port_id=_parse_port_id(to_port_id),
            cable_type=cable_type,
            length=length,
            colour=colour,
            route_notes=route_notes,
            installed_date=_parse_date(installed_date),
            last_tested_status=last_tested_status,
            last_tested_date=_parse_date(last_tested_date),
            cable_supplied_by=cable_supplied_by,
            status=status,
        )

        return RedirectResponse(
            url="/cables",
            status_code=303,
        )

    except ValueError as exc:
        return templates.TemplateResponse(
            request=request,
            name="cables/create.html",
            context=build_template_context(
                title="Create Cable",
                current_user=current_user,
                db=db,
                current_location=current_location,
                ports=CableService.list_ports_for_location(db, current_location.id),
                error=str(exc),
                form_data={
                    "cable_id": cable_id,
                    "from_port_id": from_port_id,
                    "to_port_id": to_port_id,
                    "cable_type": cable_type,
                    "length": length,
                    "colour": colour,
                    "route_notes": route_notes,
                    "installed_date": installed_date,
                    "last_tested_status": last_tested_status,
                    "last_tested_date": last_tested_date,
                    "cable_supplied_by": cable_supplied_by,
                    "status": status,
                },
            ),
            status_code=400,
        )


@router.get("/{cable_pk}", response_class=HTMLResponse)
async def detail_cable(
    cable_pk: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cable = CableService.get_cable(db, cable_pk)

    if cable is None:
        return RedirectResponse(
            url="/cables",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="cables/detail.html",
        context=build_template_context(
            title=f"Cable {cable.cable_id}",
            current_user=current_user,
            db=db,
            current_location=LocationService.get_location(db, cable.location_id),
            cable=cable,
        ),
    )


@router.get("/{cable_pk}/edit", response_class=HTMLResponse)
async def edit_cable_form(
    cable_pk: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    cable = CableService.get_cable(db, cable_pk)

    if cable is None:
        return RedirectResponse(
            url="/cables",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="cables/edit.html",
        context=build_template_context(
            title=f"Edit Cable {cable.cable_id}",
            current_user=current_user,
            db=db,
            current_location=LocationService.get_location(db, cable.location_id),
            cable=cable,
            ports=CableService.list_ports_for_location(db, cable.location_id),
            error=None,
        ),
    )


@router.post("/{cable_pk}/edit")
async def edit_cable_submit(
    cable_pk: int,
    request: Request,
    cable_id: str = Form(...),
    from_port_id: str = Form(""),
    to_port_id: str = Form(""),
    cable_type: str = Form(""),
    length: str = Form(""),
    colour: str = Form(""),
    route_notes: str = Form(""),
    installed_date: str = Form(""),
    last_tested_status: str = Form(""),
    last_tested_date: str = Form(""),
    cable_supplied_by: str = Form(""),
    status: str = Form("active"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    cable = CableService.get_cable(db, cable_pk)

    if cable is None:
        return RedirectResponse(
            url="/cables",
            status_code=303,
        )

    try:
        CableService.update_cable(
            db,
            cable=cable,
            cable_id=cable_id,
            from_port_id=_parse_port_id(from_port_id),
            to_port_id=_parse_port_id(to_port_id),
            cable_type=cable_type,
            length=length,
            colour=colour,
            route_notes=route_notes,
            installed_date=_parse_date(installed_date),
            last_tested_status=last_tested_status,
            last_tested_date=_parse_date(last_tested_date),
            cable_supplied_by=cable_supplied_by,
            status=status,
        )

        return RedirectResponse(
            url="/cables",
            status_code=303,
        )

    except ValueError as exc:
        return templates.TemplateResponse(
            request=request,
            name="cables/edit.html",
            context=build_template_context(
                title=f"Edit Cable {cable.cable_id}",
                current_user=current_user,
                db=db,
                current_location=LocationService.get_location(db, cable.location_id),
                cable=cable,
                ports=CableService.list_ports_for_location(db, cable.location_id),
                error=str(exc),
                form_data={
                    "cable_id": cable_id,
                    "from_port_id": from_port_id,
                    "to_port_id": to_port_id,
                    "cable_type": cable_type,
                    "length": length,
                    "colour": colour,
                    "route_notes": route_notes,
                    "installed_date": installed_date,
                    "last_tested_status": last_tested_status,
                    "last_tested_date": last_tested_date,
                    "cable_supplied_by": cable_supplied_by,
                    "status": status,
                },
            ),
            status_code=400,
        )


@router.post("/{cable_pk}/delete")
async def delete_cable(
    cable_pk: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    cable = CableService.get_cable(db, cable_pk)

    if cable is None:
        return RedirectResponse(
            url="/cables",
            status_code=303,
        )

    CableService.delete_cable(
        db,
        cable,
    )

    return RedirectResponse(
        url="/cables",
        status_code=303,
    )