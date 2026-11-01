from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from models import User
from repositories.users_repository import UsersRepository


class UserService:

    def __init__(self, session):
        self.session = session
        self.repository = UsersRepository(session)

    def get_users(self):
        return self.repository.get_all()

    def get_user_by_id(self, user_id):

        user = self.repository.get_by_id(user_id)

        if user is None:
            raise LookupError("User not found.")

        return user

    def create_user(
        self,
        name,
        last_name,
        email,
        password,
        role="CLIENT"
    ):

        email = email.strip().lower()

        existing_user = (
            self.repository.get_by_email(email)
        )

        if existing_user:
            raise ValueError(
                "Email is already registered."
            )

        if role not in {"CLIENT", "ADMIN"}:
            raise ValueError(
                "Invalid role."
            )

        user = User(
            name=name.strip(),
            last_name=last_name.strip(),
            email=email,
            password_hash=generate_password_hash(
                password
            ),
            role=role,
        )

        try:
            self.repository.create(user)

            self.session.commit()

            return user

        except Exception:
            self.session.rollback()
            raise

    def update_user(self, user_id, data):

        user = self.get_user_by_id(user_id)

        allowed_fields = {
            "name",
            "last_name",
            "email",
            "password",
            "role",
        }

        invalid_fields = set(data) - allowed_fields

        if invalid_fields:
            raise ValueError(
                f"Invalid fields: {', '.join(invalid_fields)}"
            )

        if "email" in data:
            email = data["email"].strip().lower()

            existing_user = self.repository.get_by_email(email)

            if existing_user and existing_user.id != user_id:
                raise ValueError("Email is already registered.")

            user.email = email

        if "name" in data:
            user.name = data["name"].strip()

        if "last_name" in data:
            user.last_name = data["last_name"].strip()

        if "password" in data:
            user.password_hash = generate_password_hash(
                data["password"]
            )

        if "role" in data:

            if data["role"] not in ("CLIENT", "ADMIN"):
                raise ValueError("Invalid role.")

            user.role = data["role"]

        try:
            self.session.commit()
            return user

        except Exception:
            self.session.rollback()
            raise

    def delete_user(self, user_id):

        user = self.get_user_by_id(user_id)

        try:
            self.session.delete(user)
            self.session.commit()

        except Exception:
            self.session.rollback()
            raise
    
    def change_password(
        self,
        user_id,
        current_password,
        new_password
    ):
        user = self.get_user_by_id(user_id)

        if not check_password_hash(
            user.password_hash,
            current_password
        ):
            raise ValueError("Current password is incorrect.")

        if len(new_password) < 8:
            raise ValueError(
                "New password must contain at least 8 characters."
            )

        if len(new_password) > 128:
            raise ValueError(
                "New password cannot exceed 128 characters."
            )

        if check_password_hash(
            user.password_hash,
            new_password
        ):
            raise ValueError(
                "New password must be different from the current password."
            )

        try:
            user.password_hash = generate_password_hash(
                new_password
            )

            self.session.commit()

            return True

        except Exception:
            self.session.rollback()
            raise
