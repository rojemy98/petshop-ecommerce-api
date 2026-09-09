from sqlalchemy import select
from sqlalchemy.orm import Session

from models import BillingAddress
from repositories.base_repository import BaseRepository


class BillingAddressesRepository(
    BaseRepository[BillingAddress]
):

    def __init__(self, session: Session):
        super().__init__(
            session,
            BillingAddress
        )

    def get_by_user_id(
        self,
        user_id: int
    ) -> list[BillingAddress]:

        statement = select(BillingAddress).where(
            BillingAddress.user_id == user_id
        )

        return list(
            self.session.execute(statement)
            .scalars()
            .all()
        )