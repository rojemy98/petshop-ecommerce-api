from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from models.cart import Cart
from models.cart_product import CartProduct
from repositories.base_repository import BaseRepository


class CartsRepository(BaseRepository[Cart]):

    def __init__(self, session: Session):
        super().__init__(session, Cart)

    def get_active_cart_by_user(
        self,
        user_id: int
    ) -> Cart | None:

        statement = (
            select(self.model)
            .where(
                self.model.user_id == user_id,
                self.model.status == "ACTIVE"
            )
            .options(
                selectinload(self.model.cart_products)
                .selectinload(CartProduct.product)
            )
        )

        return self.session.execute(
            statement
        ).scalar_one_or_none()

    def get_cart_with_products(
        self,
        cart_id: int
    ) -> Cart | None:

        statement = (
            select(self.model)
            .where(
                self.model.id == cart_id
            )
            .options(
                selectinload(self.model.cart_products)
                .selectinload(CartProduct.product)
            )
        )

        return self.session.execute(
            statement
        ).scalar_one_or_none()

    def get_carts_by_user(
        self,
        user_id: int
    ) -> list[Cart]:

        statement = (
            select(self.model)
            .where(
                self.model.user_id == user_id
            )
            .options(
                selectinload(self.model.cart_products)
                .selectinload(CartProduct.product)
            )
            .order_by(
                self.model.created_at.desc()
            )
        )

        return list(
            self.session.execute(
                statement
            ).scalars().all()
        )

    def get_cart_product(
        self,
        cart_id: int,
        product_id: int
    ) -> CartProduct | None:

        statement = select(CartProduct).where(
            CartProduct.cart_id == cart_id,
            CartProduct.product_id == product_id
        )

        return self.session.execute(
            statement
        ).scalar_one_or_none()

    def add_cart_product(
        self,
        cart_product: CartProduct
    ) -> CartProduct:

        self.session.add(cart_product)
        self.session.flush()

        return cart_product

    def delete_cart_product(
        self,
        cart_product: CartProduct
    ) -> None:

        self.session.delete(cart_product)
        self.session.flush()