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
                f"Invalid fields: {', '.join(sorted(invalid_fields))}"
            )

        validated_data = {}

        # Validate name
        if "name" in data:
            name = data["name"]

            if not isinstance(name, str) or not name.strip():
                raise ValueError("Name must be a non-empty string.")

            if len(name.strip()) > 100:
                raise ValueError("Name cannot exceed 100 characters.")

            validated_data["name"] = name.strip()

        # Validate last name
        if "last_name" in data:
            last_name = data["last_name"]

            if not isinstance(last_name, str) or not last_name.strip():
                raise ValueError("Last name must be a non-empty string.")

            if len(last_name.strip()) > 100:
                raise ValueError("Last name cannot exceed 100 characters.")

            validated_data["last_name"] = last_name.strip()

        # Validate email
        if "email" in data:
            email = data["email"]

            if not isinstance(email, str) or not email.strip():
                raise ValueError("Email must be a non-empty string.")

            email = email.strip().lower()

            if len(email) > 150 or "@" not in email:
                raise ValueError("Invalid email address.")

            existing_user = self.repository.get_by_email(email)

            if existing_user and existing_user.id != user_id:
                raise ValueError("Email is already registered.")

            validated_data["email"] = email

        # Validate password
        if "password" in data:
            password = data["password"]

            if not isinstance(password, str):
                raise ValueError("Password must be a string.")

            if len(password) < 8 or len(password) > 128:
                raise ValueError(
                    "Password must contain between 8 and 128 characters."
                )

            validated_data["password"] = password

        # Validate role
        if "role" in data:
            role = data["role"]

            if role not in {"ADMIN", "CLIENT"}:
                raise ValueError("Invalid role.")

            validated_data["role"] = role

        try:
            if "name" in validated_data:
                user.name = validated_data["name"]

            if "last_name" in validated_data:
                user.last_name = validated_data["last_name"]

            if "email" in validated_data:
                user.email = validated_data["email"]

            if "password" in validated_data:
                user.password_hash = generate_password_hash(
                    validated_data["password"]
                )

            if "role" in validated_data:
                user.role = validated_data["role"]

            self.session.commit()

            return user

        except Exception:
            self.session.rollback()
            raise

    def delete_user(self, user_id, requesting_user_id):

        user = self.get_user_by_id(user_id)

        if user_id == requesting_user_id:
            raise ValueError(
                "You cannot deactivate your own account."
            )

        if not user.is_active:
            raise ValueError(
                "User is already inactive."
            )

        if user.role == "ADMIN":

            admin_count = (
                self.session.query(User)
                .filter(
                    User.role == "ADMIN",
                    User.is_active.is_(True)
                )
                .count()
            )

            if admin_count <= 1:
                raise ValueError(
                    "Cannot deactivate the last active administrator."
                )

        try:
            user.is_active = False
            user.token_version += 1

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

            user.token_version += 1

            self.session.commit()

            return True

        except Exception:
            self.session.rollback()
            raise

    def revoke_user_sessions(self, user_id: int):
        user = self.session.get(User, user_id)

        if not user:
            raise LookupError("User not found.")

        try:
            user.token_version += 1
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
