from sqlalchemy import select
from sqlalchemy.orm import Session

from models.payment import Payment
from repositories.base_repository import BaseRepository


class PaymentsRepository(BaseRepository[Payment]):

    def __init__(self, session: Session):
        super().__init__(session, Payment)

    def get_by_invoice_id(
        self,
        invoice_id: int
    ) -> Payment | None:

        statement = select(self.model).where(
            self.model.invoice_id == invoice_id
        )

        return self.session.execute(
            statement
        ).scalar_one_or_none()

    def get_by_reference(
        self,
        payment_reference: str
    ) -> Payment | None:

        statement = select(self.model).where(
            self.model.payment_reference == payment_reference
        )

        return self.session.execute(
            statement
        ).scalar_one_or_none()