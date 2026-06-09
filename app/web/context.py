from typing import Any

from sqlalchemy.orm import Session

from app.models.location import Location
from app.models.user import User
from app.services.location_service import LocationService


def build_template_context(
    *,
    title: str,
    current_user: User | None = None,
    db: Session | None = None,
    current_location: Location | None = None,
    **extra: Any,
) -> dict[str, Any]:
    locations: list[Location] = []

    if db is not None:
        locations = LocationService.list_locations(db)

    if (
        current_location is None
        and db is not None
        and current_user is not None
        and current_user.selected_location_id is not None
    ):
        current_location = LocationService.get_location(
            db,
            current_user.selected_location_id,
        )

    context: dict[str, Any] = {
        "title": title,
        "current_user": current_user,
        "is_admin": (
            current_user is not None
            and current_user.is_active
            and current_user.role == "admin"
        ),
        "locations": locations,
        "current_location": current_location,
    }

    context.update(extra)

    return context