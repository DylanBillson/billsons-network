from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.web.context import build_template_context


router = APIRouter()

templates = Jinja2Templates(
    directory="app/web/templates",
)


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=build_template_context(
            title=settings.APP_NAME,
            current_user=current_user,
            db=db,
            request=request,
        ),
    )