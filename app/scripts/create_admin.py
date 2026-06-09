from app.db.session import SessionLocal
from app.models.user import User
from app.services.auth_service import AuthService


def main() -> None:
    username = input("Username: ").strip()
    display_name = input("Display Name: ").strip()
    password = input("Password: ").strip()

    with SessionLocal() as db:
        existing = AuthService.get_user_by_username(
            db,
            username,
        )

        if existing:
            print("User already exists.")
            return

        user = AuthService.create_user(
            db=db,
            username=username,
            display_name=display_name,
            plain_password=password,
            role="admin",
            is_active=True,
        )

        print()
        print("Admin user created.")
        print(f"ID: {user.id}")
        print(f"Username: {user.username}")


if __name__ == "__main__":
    main()