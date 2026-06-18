from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import get_db
from app.core.session import SESSION_COOKIE_NAME, read_session_token
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
):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    user_id = read_session_token(token)

    if user_id is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    current_user = db.get(User, user_id)

    if (
        current_user is None
        or not current_user.is_active
        or current_user.is_deleted
    ):
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=build_template_context(
            title=settings.APP_NAME,
            current_user=current_user,
            db=db,
        ),
    )