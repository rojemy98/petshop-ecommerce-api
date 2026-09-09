from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from models import Return, ReturnProduct, Invoice
from repositories.base_repository import BaseRepository


class ReturnsRepository(BaseRepository[Return]):

    def __init__(self, session: Session):
        super().__init__(
            session,
            Return
        )

    def get_with_products(
        self,
        return_id: int
    ) -> Return | None:

        statement = (
            select(Return)
            .options(
                selectinload(
                    Return.return_products
                ).selectinload(
                    ReturnProduct.invoice_product
                ),
                selectinload(
                    Return.invoice
                )
            )
            .where(
                Return.id == return_id
            )
        )

        return (
            self.session.execute(statement)
            .scalar_one_or_none()
        )

    def get_by_user_id(
        self,
        user_id: int
    ) -> list[Return]:

        statement = (
            select(Return)
            .join(
                Invoice,
                Return.invoice_id == Invoice.id
            )
            .options(
                selectinload(
                    Return.return_products
                ),
                selectinload(
                    Return.invoice
                )
            )
            .where(
                Invoice.user_id == user_id
            )
            .order_by(
                Return.created_at.desc()
            )
        )

        return list(
            self.session.execute(statement)
            .scalars()
            .all()
        )

    def get_by_invoice(
        self,
        invoice_id: int
    ) -> list[Return]:

        statement = (
            select(Return)
            .options(
                selectinload(
                    Return.return_products
                ),
                selectinload(
                    Return.invoice
                )
            )
            .where(
                Return.invoice_id == invoice_id
            )
            .order_by(
                Return.created_at.desc()
            )
        )

        return list(
            self.session.execute(statement)
            .scalars()
            .all()
        )

    def get_all_with_products(
        self
    ) -> list[Return]:

        statement = (
            select(Return)
            .options(
                selectinload(
                    Return.return_products
                ),
                selectinload(
                    Return.invoice
                )
            )
            .order_by(
                Return.created_at.desc()
            )
        )

        return list(
            self.session.execute(statement)
            .scalars()
            .all()
        )