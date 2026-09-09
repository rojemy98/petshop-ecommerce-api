from sqlalchemy import select
from sqlalchemy.orm import Session

from models.user import User
from repositories.base_repository import BaseRepository


class UsersRepository(BaseRepository[User]):

    def __init__(self, session: Session):
        super().__init__(session, User)

    def get_by_email(self, email: str) -> User | None:
        statement = select(self.model).where(
            self.model.email == email
        )

        return self.session.execute(statement).scalar_one_or_none()