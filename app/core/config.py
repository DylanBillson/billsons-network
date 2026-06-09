from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    # ==========================================
    # Application
    # ==========================================

    APP_ENV: str = Field(default="development")
    APP_NAME: str = Field(default="Billson's Network")
    SECRET_KEY: str

    # ==========================================
    # Encryption
    # ==========================================

    ENCRYPTION_KEY: str

    # ==========================================
    # Database
    # ==========================================

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DATABASE_URL: str

    # ==========================================
    # Session
    # ==========================================

    SESSION_TIMEOUT_MINUTES: int = Field(default=480)

    # ==========================================
    # Upload Limits
    # ==========================================

    DEVICE_PHOTO_MAX_MB: int = Field(default=5)
    ICON_UPLOAD_MAX_MB: int = Field(default=2)

    # ==========================================
    # Timezone
    # ==========================================

    DEFAULT_TIMEZONE: str = Field(default="UTC")


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance.

    Usage:
        settings = get_settings()
    """
    return Settings()


settings = get_settings()