from itsdangerous import BadSignature, URLSafeSerializer

from app.core.config import settings


LOCATION_COOKIE_NAME = "billsons_network_location"


def get_location_serializer() -> URLSafeSerializer:
    return URLSafeSerializer(
        secret_key=settings.SECRET_KEY,
        salt="billsons-network-location",
    )


def create_location_token(location_id: int) -> str:
    return get_location_serializer().dumps(
        {
            "location_id": location_id,
        }
    )


def read_location_token(token: str | None) -> int | None:
    if not token:
        return None

    try:
        data = get_location_serializer().loads(token)
    except BadSignature:
        return None

    location_id = data.get("location_id")

    if not isinstance(location_id, int):
        return None

    return location_id