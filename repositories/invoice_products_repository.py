from sqlalchemy.orm import Session

from models import InvoiceProduct
from repositories.base_repository import BaseRepository


class InvoiceProductsRepository(
    BaseRepository[InvoiceProduct]
):

    def __init__(self, session: Session):
        super().__init__(
            session,
            InvoiceProduct
        )