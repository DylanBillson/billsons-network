from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.session import SESSION_COOKIE_NAME, create_session_token
from app.models.audit_log import AuditLog
from app.services.auth_service import AuthService


router = APIRouter()

templates = Jinja2Templates(directory="app/web/templates")


@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={
            "title": "Login",
            "error": None,
        },
    )


@router.post("/login")
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = AuthService.authenticate_user(
        db=db,
        username=username,
        plain_password=password,
    )

    if user is None:
        db.add(
            AuditLog(
                user_id=None,
                username_snapshot=username.strip(),
                action="failed_login",
                entity_type="user",
                entity_id=None,
                details="Failed login attempt.",
                ip_address=request.client.host if request.client else None,
            )
        )
        db.commit()

        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={
                "title": "Login",
                "error": "Invalid username or password.",
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    user.last_login_at = datetime.now(timezone.utc)

    db.add(
        AuditLog(
            user_id=user.id,
            username_snapshot=user.username,
            action="login",
            entity_type="user",
            entity_id=user.id,
            details="User logged in.",
            ip_address=request.client.host if request.client else None,
        )
    )

    db.add(user)
    db.commit()

    response = RedirectResponse(
        url="/",
        status_code=status.HTTP_303_SEE_OTHER,
    )

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=create_session_token(user.id),
        httponly=True,
        samesite="lax",
        secure=False,  # Set true later for production HTTPS-only cookies.
    )

    return response


@router.post("/logout")
async def logout(request: Request):
    response = RedirectResponse(
        url="/login",
        status_code=status.HTTP_303_SEE_OTHER,
    )

    response.delete_cookie(SESSION_COOKIE_NAME)

    return response