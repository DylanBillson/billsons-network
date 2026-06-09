from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.core.session import SESSION_COOKIE_NAME, read_session_token
from app.db.session import SessionLocal
from app.models.user import User
from app.web.context import build_template_context
from app.web.routes.auth import router as auth_router


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

templates = Jinja2Templates(
    directory="app/web/templates",
)

app.include_router(auth_router)


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "application": settings.APP_NAME,
        "environment": settings.APP_ENV,
    }


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    user_id = read_session_token(token)

    if user_id is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    with SessionLocal() as db:
        user = db.get(User, user_id)

        if user is None or not user.is_active or user.is_deleted:
            return RedirectResponse(
                url="/login",
                status_code=303,
            )

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context=build_template_context(
                title=settings.APP_NAME,
                current_user=user,
            ),
        )