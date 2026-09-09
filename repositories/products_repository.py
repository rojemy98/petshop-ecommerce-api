from sqlalchemy import select
from sqlalchemy.orm import Session

from models.product import Product
from repositories.base_repository import BaseRepository


class ProductsRepository(BaseRepository[Product]):

    def __init__(self, session: Session):
        super().__init__(session, Product)

    def get_by_name(self, name: str) -> Product | None:
        statement = select(self.model).where(
            self.model.name == name
        )

        return self.session.execute(statement).scalar_one_or_none()

    def get_available_products(self) -> list[Product]:
        statement = select(self.model).where(
            self.model.stock > 0,
            self.model.is_active.is_(True)
        )

        return list(
            self.session.execute(statement)
            .scalars()
            .all()
        )