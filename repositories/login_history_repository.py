from sqlalchemy import select
from sqlalchemy.orm import Session

from models.login_history import LoginHistory
from repositories.base_repository import BaseRepository


class LoginHistoryRepository(BaseRepository[LoginHistory]):

    def __init__(self, session: Session):
        super().__init__(session, LoginHistory)

    def get_by_user(
        self,
        user_id: int
    ) -> list[LoginHistory]:

        statement = (
            select(self.model)
            .where(
                self.model.user_id == user_id
            )
            .order_by(
                self.model.created_at.desc()
            )
        )

        return list(
            self.session.execute(statement)
            .scalars()
            .all()
        )