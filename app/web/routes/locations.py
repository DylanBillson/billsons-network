from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_user,
    get_db,
    require_admin,
)
from app.models.user import User
from app.services.location_service import LocationService
from app.web.context import build_template_context


router = APIRouter(
    prefix="/admin/locations",
    tags=["admin-locations"],
)

templates = Jinja2Templates(
    directory="app/web/templates",
)


@router.get("", response_class=HTMLResponse)
async def list_locations(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    locations = LocationService.list_locations(db)

    return templates.TemplateResponse(
        request=request,
        name="admin/locations/list.html",
        context=build_template_context(
            title="Locations",
            current_user=current_user,
            db=db,
            request=request,
            locations=locations,
        ),
    )


@router.get("/create", response_class=HTMLResponse)
async def create_location_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return templates.TemplateResponse(
        request=request,
        name="admin/locations/create.html",
        context=build_template_context(
            title="Create Location",
            current_user=current_user,
            db=db,
            request=request,
            error=None,
        ),
    )


@router.post("/create")
async def create_location_submit(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    notes: str = Form(""),
    address: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        location = LocationService.create_location(
            db,
            name=name,
            description=description,
            notes=notes,
            address=address,
        )

        if current_user.selected_location_id is None:
            current_user.selected_location_id = location.id
            db.add(current_user)
            db.commit()

        return RedirectResponse(
            url="/admin/locations",
            status_code=303,
        )

    except ValueError as exc:
        return templates.TemplateResponse(
            request=request,
            name="admin/locations/create.html",
            context=build_template_context(
                title="Create Location",
                current_user=current_user,
                db=db,
                request=request,
                error=str(exc),
                form_data={
                    "name": name,
                    "description": description,
                    "notes": notes,
                    "address": address,
                },
            ),
            status_code=400,
        )


@router.post("/select/{location_id}")
async def select_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    location = LocationService.get_location(
        db,
        location_id,
    )

    if location is None:
        return RedirectResponse(
            url="/",
            status_code=303,
        )

    current_user.selected_location_id = location.id

    db.add(current_user)
    db.commit()

    return RedirectResponse(
        url="/",
        status_code=303,
    )


@router.get("/{location_id}/edit", response_class=HTMLResponse)
async def edit_location_form(
    location_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    location = LocationService.get_location(
        db,
        location_id,
    )

    if location is None:
        return RedirectResponse(
            url="/admin/locations",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="admin/locations/edit.html",
        context=build_template_context(
            title="Edit Location",
            current_user=current_user,
            db=db,
            request=request,
            location=location,
            error=None,
        ),
    )


@router.post("/{location_id}/edit")
async def edit_location_submit(
    location_id: int,
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    notes: str = Form(""),
    address: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    location = LocationService.get_location(
        db,
        location_id,
    )

    if location is None:
        return RedirectResponse(
            url="/admin/locations",
            status_code=303,
        )

    try:
        LocationService.update_location(
            db,
            location=location,
            name=name,
            description=description,
            notes=notes,
            address=address,
        )

        return RedirectResponse(
            url="/admin/locations",
            status_code=303,
        )

    except ValueError as exc:
        location.name = name
        location.description = description
        location.notes = notes
        location.address = address

        return templates.TemplateResponse(
            request=request,
            name="admin/locations/edit.html",
            context=build_template_context(
                title="Edit Location",
                current_user=current_user,
                db=db,
                request=request,
                location=location,
                error=str(exc),
            ),
            status_code=400,
        )


@router.post("/{location_id}/delete")
async def delete_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    location = LocationService.get_location(
        db,
        location_id,
    )

    if location is None:
        return RedirectResponse(
            url="/admin/locations",
            status_code=303,
        )

    try:
        LocationService.delete_location(
            db,
            location,
        )

        if current_user.selected_location_id == location_id:
            current_user.selected_location_id = None
            db.add(current_user)
            db.commit()

    except ValueError:
        return RedirectResponse(
            url="/admin/locations",
            status_code=303,
        )

    return RedirectResponse(
        url="/admin/locations",
        status_code=303,
    )