from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User


class AuthService:
    """
    Authentication and user account service.

    Keeps password hashing and login checks out of route files.
    """

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User | None:
        normalized_username = username.strip()

        if not normalized_username:
            return None

        return db.scalar(
            select(User).where(
                User.username == normalized_username,
                User.is_deleted.is_(False),
            )
        )

    @staticmethod
    def authenticate_user(
        db: Session,
        username: str,
        plain_password: str,
    ) -> User | None:
        user = AuthService.get_user_by_username(db, username)

        if user is None:
            return None

        if not user.is_active:
            return None

        if not verify_password(plain_password, user.password_hash):
            return None

        return user

    @staticmethod
    def create_user(
        db: Session,
        username: str,
        display_name: str,
        plain_password: str,
        role: str = "user",
        is_active: bool = True,
    ) -> User:
        normalized_username = username.strip()
        normalized_display_name = display_name.strip()

        if role not in {"admin", "user"}:
            raise ValueError("Invalid user role.")

        if not normalized_username:
            raise ValueError("Username is required.")

        if not normalized_display_name:
            raise ValueError("Display name is required.")

        if not plain_password:
            raise ValueError("Password is required.")

        existing_user = AuthService.get_user_by_username(db, normalized_username)

        if existing_user is not None:
            raise ValueError("Username is already in use.")

        user = User(
            username=normalized_username,
            display_name=normalized_display_name,
            password_hash=hash_password(plain_password),
            role=role,
            is_active=is_active,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def change_password(
        db: Session,
        user: User,
        new_plain_password: str,
    ) -> User:
        if not new_plain_password:
            raise ValueError("Password is required.")

        user.password_hash = hash_password(new_plain_password)

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def is_admin(user: User | None) -> bool:
        return user is not None and user.role == "admin" and user.is_active