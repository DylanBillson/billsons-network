from cryptography.fernet import Fernet, InvalidToken
from passlib.context import CryptContext

from app.core.config import settings


password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password for storage.

    Plaintext passwords must never be stored.
    """
    return password_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """
    Verify a plaintext password against a stored password hash.
    """
    return password_context.verify(plain_password, password_hash)


def get_fernet() -> Fernet:
    """
    Return a Fernet instance using the configured encryption key.

    ENCRYPTION_KEY must be a valid Fernet key.
    Generate one with:

        python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    """
    return Fernet(settings.ENCRYPTION_KEY.encode())


def encrypt_text(plain_text: str | None) -> str | None:
    """
    Encrypt sensitive text for database storage.

    Used for SSID passwords.
    """
    if plain_text is None:
        return None

    if plain_text == "":
        return ""

    fernet = get_fernet()
    return fernet.encrypt(plain_text.encode()).decode()


def decrypt_text(encrypted_text: str | None) -> str | None:
    """
    Decrypt sensitive text from database storage.

    Used for admin-only SSID password reveal.
    """
    if encrypted_text is None:
        return None

    if encrypted_text == "":
        return ""

    fernet = get_fernet()

    try:
        return fernet.decrypt(encrypted_text.encode()).decode()
    except InvalidToken:
        raise ValueError("Unable to decrypt value. Check ENCRYPTION_KEY.")