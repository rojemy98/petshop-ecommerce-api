from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from models import Invoice, InvoiceProduct
from repositories.base_repository import BaseRepository


class InvoicesRepository(BaseRepository[Invoice]):

    def __init__(self, session: Session):
        super().__init__(
            session,
            Invoice
        )

    def get_by_invoice_number(
        self,
        invoice_number: str
    ) -> Invoice | None:

        statement = (
            select(Invoice)
            .options(
                selectinload(
                    Invoice.invoice_products
                ).selectinload(
                    InvoiceProduct.product
                ),
                selectinload(
                    Invoice.payment
                )
            )
            .where(
                Invoice.invoice_number
                == invoice_number
            )
        )

        return (
            self.session.execute(statement)
            .scalar_one_or_none()
        )

    def get_by_user_id(
        self,
        user_id: int
    ) -> list[Invoice]:

        statement = (
            select(Invoice)
            .options(
                selectinload(
                    Invoice.invoice_products
                ).selectinload(
                    InvoiceProduct.product
                ),
                selectinload(
                    Invoice.payment
                )
            )
            .where(
                Invoice.user_id == user_id
            )
            .order_by(
                Invoice.purchase_date.desc()
            )
        )

        return list(
            self.session.execute(statement)
            .scalars()
            .all()
        )

    def get_all_with_details(
        self
    ) -> list[Invoice]:

        statement = (
            select(Invoice)
            .options(
                selectinload(
                    Invoice.invoice_products
                ).selectinload(
                    InvoiceProduct.product
                ),
                selectinload(
                    Invoice.payment
                )
            )
            .order_by(
                Invoice.purchase_date.desc()
            )
        )

        return list(
            self.session.execute(statement)
            .scalars()
            .all()
        )

    def get_by_id_with_details(
        self,
        invoice_id: int
    ) -> Invoice | None:

        statement = (
            select(Invoice)
            .options(
                selectinload(
                    Invoice.invoice_products
                ).selectinload(
                    InvoiceProduct.product
                ),
                selectinload(
                    Invoice.returns
                )
            )
            .where(
                Invoice.id == invoice_id
            )
        )

        return (
            self.session.execute(statement)
            .scalar_one_or_none()
        )