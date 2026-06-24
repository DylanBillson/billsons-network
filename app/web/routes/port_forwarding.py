from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_admin
from app.models.user import User
from app.services.location_service import LocationService
from app.services.port_forwarding_service import PortForwardingService
from app.web.context import build_template_context


router = APIRouter(
    prefix="/devices",
    tags=["port-forwarding"],
)

templates = Jinja2Templates(
    directory="app/web/templates",
)


def _parse_optional_int(
    value: str,
) -> int | None:
    if not value:
        return None

    return int(value)


def _parse_bool(
    value: str | None,
) -> bool:
    return value == "true"


@router.get("/{router_device_id}/port-forwarding", response_class=HTMLResponse)
async def list_port_forwarding_rules(
    router_device_id: int,
    request: Request,
    error: str = Query(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    router_device = PortForwardingService.get_router_device(
        db,
        router_device_id,
    )

    if router_device is None:
        return RedirectResponse(
            url="/devices",
            status_code=303,
        )

    if not PortForwardingService.is_router_device(router_device):
        query_string = urlencode(
            {
                "error": "Port forwarding rules can only be managed on router devices.",
            }
        )

        return RedirectResponse(
            url=f"/devices/{router_device.id}?{query_string}",
            status_code=303,
        )

    rules = PortForwardingService.list_rules_for_router(
        db,
        router_device.id,
    )

    return templates.TemplateResponse(
        request=request,
        name="port_forwarding/list.html",
        context=build_template_context(
            title=f"Port Forwarding - {router_device.name}",
            current_user=current_user,
            db=db,
            current_location=LocationService.get_location(
                db,
                router_device.location_id,
            ),
            router_device=router_device,
            rules=rules,
            error=error,
        ),
    )


@router.get("/{router_device_id}/port-forwarding/create", response_class=HTMLResponse)
async def create_port_forwarding_rule_form(
    router_device_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    router_device = PortForwardingService.get_router_device(
        db,
        router_device_id,
    )

    if router_device is None:
        return RedirectResponse(
            url="/devices",
            status_code=303,
        )

    if not PortForwardingService.is_router_device(router_device):
        return RedirectResponse(
            url=f"/devices/{router_device.id}",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="port_forwarding/create.html",
        context=build_template_context(
            title=f"Create Port Forwarding Rule - {router_device.name}",
            current_user=current_user,
            db=db,
            current_location=LocationService.get_location(
                db,
                router_device.location_id,
            ),
            router_device=router_device,
            error=None,
        ),
    )


@router.post("/{router_device_id}/port-forwarding/create")
async def create_port_forwarding_rule_submit(
    router_device_id: int,
    request: Request,
    rule_name: str = Form(...),
    external_port_start: int = Form(...),
    external_port_end: str = Form(""),
    internal_ip_address: str = Form(...),
    internal_port_start: int = Form(...),
    internal_port_end: str = Form(""),
    protocol: str = Form("tcp"),
    is_enabled: str | None = Form(None),
    notes: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    router_device = PortForwardingService.get_router_device(
        db,
        router_device_id,
    )

    if router_device is None:
        return RedirectResponse(
            url="/devices",
            status_code=303,
        )

    try:
        PortForwardingService.create_rule(
            db,
            router_device_id=router_device.id,
            rule_name=rule_name,
            external_port_start=external_port_start,
            external_port_end=_parse_optional_int(external_port_end),
            internal_ip_address=internal_ip_address,
            internal_port_start=internal_port_start,
            internal_port_end=_parse_optional_int(internal_port_end),
            protocol=protocol,
            is_enabled=_parse_bool(is_enabled),
            notes=notes,
        )

        return RedirectResponse(
            url=f"/devices/{router_device.id}/port-forwarding",
            status_code=303,
        )

    except ValueError as exc:
        return templates.TemplateResponse(
            request=request,
            name="port_forwarding/create.html",
            context=build_template_context(
                title=f"Create Port Forwarding Rule - {router_device.name}",
                current_user=current_user,
                db=db,
                current_location=LocationService.get_location(
                    db,
                    router_device.location_id,
                ),
                router_device=router_device,
                error=str(exc),
                form_data={
                    "rule_name": rule_name,
                    "external_port_start": external_port_start,
                    "external_port_end": external_port_end,
                    "internal_ip_address": internal_ip_address,
                    "internal_port_start": internal_port_start,
                    "internal_port_end": internal_port_end,
                    "protocol": protocol,
                    "is_enabled": is_enabled,
                    "notes": notes,
                },
            ),
            status_code=400,
        )


@router.get("/{router_device_id}/port-forwarding/{rule_id}/edit", response_class=HTMLResponse)
async def edit_port_forwarding_rule_form(
    router_device_id: int,
    rule_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    router_device = PortForwardingService.get_router_device(
        db,
        router_device_id,
    )

    rule = PortForwardingService.get_rule(
        db,
        rule_id,
    )

    if (
        router_device is None
        or rule is None
        or rule.router_device_id != router_device.id
    ):
        return RedirectResponse(
            url="/devices",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="port_forwarding/edit.html",
        context=build_template_context(
            title=f"Edit Port Forwarding Rule - {router_device.name}",
            current_user=current_user,
            db=db,
            current_location=LocationService.get_location(
                db,
                router_device.location_id,
            ),
            router_device=router_device,
            rule=rule,
            error=None,
        ),
    )


@router.post("/{router_device_id}/port-forwarding/{rule_id}/edit")
async def edit_port_forwarding_rule_submit(
    router_device_id: int,
    rule_id: int,
    request: Request,
    rule_name: str = Form(...),
    external_port_start: int = Form(...),
    external_port_end: str = Form(""),
    internal_ip_address: str = Form(...),
    internal_port_start: int = Form(...),
    internal_port_end: str = Form(""),
    protocol: str = Form("tcp"),
    is_enabled: str | None = Form(None),
    notes: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    router_device = PortForwardingService.get_router_device(
        db,
        router_device_id,
    )

    rule = PortForwardingService.get_rule(
        db,
        rule_id,
    )

    if (
        router_device is None
        or rule is None
        or rule.router_device_id != router_device.id
    ):
        return RedirectResponse(
            url="/devices",
            status_code=303,
        )

    try:
        PortForwardingService.update_rule(
            db,
            rule=rule,
            rule_name=rule_name,
            external_port_start=external_port_start,
            external_port_end=_parse_optional_int(external_port_end),
            internal_ip_address=internal_ip_address,
            internal_port_start=internal_port_start,
            internal_port_end=_parse_optional_int(internal_port_end),
            protocol=protocol,
            is_enabled=_parse_bool(is_enabled),
            notes=notes,
        )

        return RedirectResponse(
            url=f"/devices/{router_device.id}/port-forwarding",
            status_code=303,
        )

    except ValueError as exc:
        return templates.TemplateResponse(
            request=request,
            name="port_forwarding/edit.html",
            context=build_template_context(
                title=f"Edit Port Forwarding Rule - {router_device.name}",
                current_user=current_user,
                db=db,
                current_location=LocationService.get_location(
                    db,
                    router_device.location_id,
                ),
                router_device=router_device,
                rule=rule,
                error=str(exc),
            ),
            status_code=400,
        )


@router.post("/{router_device_id}/port-forwarding/{rule_id}/delete")
async def delete_port_forwarding_rule(
    router_device_id: int,
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    router_device = PortForwardingService.get_router_device(
        db,
        router_device_id,
    )

    rule = PortForwardingService.get_rule(
        db,
        rule_id,
    )

    if (
        router_device is None
        or rule is None
        or rule.router_device_id != router_device.id
    ):
        return RedirectResponse(
            url="/devices",
            status_code=303,
        )

    PortForwardingService.delete_rule(
        db,
        rule,
    )

    return RedirectResponse(
        url=f"/devices/{router_device.id}/port-forwarding",
        status_code=303,
    )