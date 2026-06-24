from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_admin
from app.models.user import User
from app.web.context import build_template_context


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

templates = Jinja2Templates(
    directory="app/web/templates",
)


@router.get("", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return templates.TemplateResponse(
        request=request,
        name="admin/index.html",
        context=build_template_context(
            title="Admin",
            current_user=current_user,
            db=db,
        ),
    )