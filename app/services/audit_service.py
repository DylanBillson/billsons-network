from fastapi import Request
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User


class AuditService:
    @staticmethod
    def get_request_ip(
        request: Request,
    ) -> str | None:
        forwarded_for = request.headers.get("x-forwarded-for")

        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        if request.client:
            return request.client.host

        return None

    @staticmethod
    def log_event(
        db: Session,
        *,
        user: User | None,
        action: str,
        entity_type: str | None = None,
        entity_id: int | None = None,
        details: str | None = None,
        request: Request | None = None,
    ) -> AuditLog:
        audit_log = AuditLog(
            user_id=user.id if user else None,
            username_snapshot=user.username if user else None,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=AuditService.get_request_ip(request) if request else None,
        )

        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)

        return audit_log