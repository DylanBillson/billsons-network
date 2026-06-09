from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.core.config import settings


SESSION_COOKIE_NAME = "billsons_network_session"


def get_serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(
        secret_key=settings.SECRET_KEY,
        salt="billsons-network-session",
    )


def create_session_token(user_id: int) -> str:
    serializer = get_serializer()

    return serializer.dumps(
        {
            "user_id": user_id,
        }
    )


def read_session_token(token: str | None) -> int | None:
    if not token:
        return None

    serializer = get_serializer()

    try:
        data = serializer.loads(
            token,
            max_age=settings.SESSION_TIMEOUT_MINUTES * 60,
        )
    except (BadSignature, SignatureExpired):
        return None

    user_id = data.get("user_id")

    if not isinstance(user_id, int):
        return None

    return user_id