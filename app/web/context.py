from typing import Any

from app.models.user import User


def build_template_context(
    *,
    title: str,
    current_user: User | None = None,
    current_location: Any = None,
    **extra: Any,
) -> dict[str, Any]:
    """
    Standard template context builder.

    Ensures all templates receive the same common values.
    """

    context: dict[str, Any] = {
        "title": title,
        "current_user": current_user,
        "current_location": current_location,
        "is_admin": (
            current_user is not None
            and current_user.is_active
            and current_user.role == "admin"
        ),
    }

    context.update(extra)

    return context