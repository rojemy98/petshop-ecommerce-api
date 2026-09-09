from sqlalchemy import select, func
from sqlalchemy.orm import Session

from models import ReturnProduct, Return
from repositories.base_repository import BaseRepository


class ReturnProductsRepository(
    BaseRepository[ReturnProduct]
):

    def __init__(self, session: Session):
        super().__init__(
            session,
            ReturnProduct
        )

    def get_completed_quantities(
        self,
        invoice_product_ids: list[int]
    ) -> dict[int, int]:

        if not invoice_product_ids:
            return {}

        statement = (
            select(
                ReturnProduct.invoice_product_id,
                func.sum(
                    ReturnProduct.quantity
                ).label(
                    "completed_quantity"
                )
            )
            .join(
                Return,
                Return.id
                == ReturnProduct.return_id
            )
            .where(
                ReturnProduct.invoice_product_id.in_(
                    invoice_product_ids
                ),
                Return.status == "COMPLETED"
            )
            .group_by(
                ReturnProduct.invoice_product_id
            )
        )

        rows = (
            self.session.execute(statement)
            .all()
        )

        return {
            invoice_product_id: int(quantity)
            for invoice_product_id, quantity
            in rows
        }