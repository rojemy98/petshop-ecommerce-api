from sqlalchemy.orm import Session
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from models import User, LoginHistory
from repositories import (
    UsersRepository,
    LoginHistoryRepository
)

from services.jwt_manager import JWTManager

from config import (
    load_private_key,
    load_public_key,
    JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRES
)


class AuthService:

    def __init__(
        self,
        session: Session,
        jwt_manager: JWTManager
    ):
        self.session = session
        self.users_repository = UsersRepository(session)
        self.login_history_repository = LoginHistoryRepository(session)
        self.jwt_manager = jwt_manager

    def register(
        self,
        name: str,
        last_name: str,
        email: str,
        password: str
    ) -> str:

        email = email.strip().lower()

        existing_user = self.users_repository.get_by_email(email)

        if existing_user:
            raise ValueError(
                "A user with this email already exists."
            )

        password_hash = generate_password_hash(password)

        user = User(
            name=name,
            last_name=last_name,
            email=email,
            password_hash=password_hash,
            role="CLIENT"
        )

        try:
            self.users_repository.create(user)

            self.session.commit()

            return self._generate_access_token(user)

        except Exception:
            self.session.rollback()
            raise

    def login(
        self,
        email: str,
        password: str,
        ip_address: str
    ) -> str:

        email = email.strip().lower()

        user = self.users_repository.get_by_email(email)

        if user is None:
            self._register_login_attempt(
                user_id=None,
                ip_address=ip_address,
                success=False
            )

            raise ValueError(
                "Invalid email or password."
            )

        if not check_password_hash(
            user.password_hash,
            password
        ):
            self._register_login_attempt(
                user_id=user.id,
                ip_address=ip_address,
                success=False
            )

            raise ValueError(
                "Invalid email or password."
            )

        self._register_login_attempt(
            user_id=user.id,
            ip_address=ip_address,
            success=True
        )

        return self._generate_access_token(user)

    def _register_login_attempt(
        self,
        user_id: int | None,
        ip_address: str,
        success: bool
    ) -> None:

        login_history = LoginHistory(
            user_id=user_id,
            ip_address=ip_address,
            success=success
        )

        try:
            self.login_history_repository.create(
                login_history
            )

            self.session.commit()

        except Exception:
            self.session.rollback()
            raise

    def _generate_access_token(
        self,
        user: User
    ) -> str:

        return self.jwt_manager.encode(
            {
                "id": user.id,
                "role": user.role
            }
        )