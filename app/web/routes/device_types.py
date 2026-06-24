from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_admin
from app.models.user import User
from app.services.device_type_service import DeviceTypeService
from app.web.context import build_template_context


router = APIRouter(
    prefix="/admin/device-types",
    tags=["device-types"],
)

templates = Jinja2Templates(
    directory="app/web/templates",
)


@router.get("", response_class=HTMLResponse)
async def list_device_types(
    request: Request,
    error: str = Query(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return templates.TemplateResponse(
        request=request,
        name="admin/device_types/list.html",
        context=build_template_context(
            title="Device Types",
            current_user=current_user,
            db=db,
            device_types=DeviceTypeService.list_device_types(
                db,
                include_inactive=True,
            ),
            error=error,
        ),
    )


@router.get("/create", response_class=HTMLResponse)
async def create_device_type_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return templates.TemplateResponse(
        request=request,
        name="admin/device_types/create.html",
        context=build_template_context(
            title="Create Device Type",
            current_user=current_user,
            db=db,
            error=None,
        ),
    )


@router.post("/create")
async def create_device_type_submit(
    request: Request,
    name: str = Form(...),
    slug: str = Form(...),
    description: str = Form(""),
    icon_path: str = Form(""),
    is_default: bool = Form(False),
    is_active: bool = Form(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        DeviceTypeService.create_device_type(
            db,
            name=name,
            slug=slug,
            description=description,
            icon_path=icon_path,
            is_default=is_default,
            is_active=is_active,
        )

        return RedirectResponse(
            url="/admin/device-types",
            status_code=303,
        )

    except ValueError as exc:
        return templates.TemplateResponse(
            request=request,
            name="admin/device_types/create.html",
            context=build_template_context(
                title="Create Device Type",
                current_user=current_user,
                db=db,
                error=str(exc),
                form_data={
                    "name": name,
                    "slug": slug,
                    "description": description,
                    "icon_path": icon_path,
                    "is_default": is_default,
                    "is_active": is_active,
                },
            ),
            status_code=400,
        )


@router.get("/{device_type_id}/edit", response_class=HTMLResponse)
async def edit_device_type_form(
    device_type_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    device_type = DeviceTypeService.get_device_type(
        db,
        device_type_id,
    )

    if device_type is None:
        return RedirectResponse(
            url="/admin/device-types",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="admin/device_types/edit.html",
        context=build_template_context(
            title=f"Edit {device_type.name}",
            current_user=current_user,
            db=db,
            device_type=device_type,
            error=None,
        ),
    )


@router.post("/{device_type_id}/edit")
async def edit_device_type_submit(
    device_type_id: int,
    request: Request,
    name: str = Form(...),
    slug: str = Form(...),
    description: str = Form(""),
    icon_path: str = Form(""),
    is_default: bool = Form(False),
    is_active: bool = Form(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    device_type = DeviceTypeService.get_device_type(
        db,
        device_type_id,
    )

    if device_type is None:
        return RedirectResponse(
            url="/admin/device-types",
            status_code=303,
        )

    try:
        DeviceTypeService.update_device_type(
            db,
            device_type=device_type,
            name=name,
            slug=slug,
            description=description,
            icon_path=icon_path,
            is_default=is_default,
            is_active=is_active,
        )

        return RedirectResponse(
            url="/admin/device-types",
            status_code=303,
        )

    except ValueError as exc:
        return templates.TemplateResponse(
            request=request,
            name="admin/device_types/edit.html",
            context=build_template_context(
                title=f"Edit {device_type.name}",
                current_user=current_user,
                db=db,
                device_type=device_type,
                error=str(exc),
            ),
            status_code=400,
        )


@router.post("/{device_type_id}/delete")
async def delete_device_type(
    device_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    device_type = DeviceTypeService.get_device_type(
        db,
        device_type_id,
    )

    if device_type is None:
        return RedirectResponse(
            url="/admin/device-types",
            status_code=303,
        )

    try:
        DeviceTypeService.delete_device_type(
            db,
            device_type,
        )

    except ValueError as exc:
        query_string = urlencode(
            {
                "error": str(exc),
            }
        )

        return RedirectResponse(
            url=f"/admin/device-types?{query_string}",
            status_code=303,
        )

    return RedirectResponse(
        url="/admin/device-types",
        status_code=303,
    )