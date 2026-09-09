from decimal import Decimal

from sqlalchemy.orm import Session

from models import Cart, CartProduct
from repositories import (
    CartsRepository,
    ProductsRepository,
)


class CartService:

    def __init__(self, session: Session):
        self.session = session
        self.carts_repository = CartsRepository(session)
        self.products_repository = ProductsRepository(session)

    def get_active_cart(self, user_id):

        cart = self.carts_repository.get_active_cart_by_user(user_id)

        if cart is None:
            raise LookupError("Active cart not found.")

        return cart

    def create_cart(self, user_id):

        active_cart = (
            self.carts_repository
            .get_active_cart_by_user(user_id)
        )

        if active_cart:
            raise ValueError(
                "User already has an active cart."
            )

        cart = Cart(
            user_id=user_id,
            status="ACTIVE"
        )

        try:
            self.carts_repository.create(cart)

            self.session.commit()

            return cart

        except Exception:
            self.session.rollback()
            raise

    def get_user_carts(
        self,
        user_id: int
    ) -> list[Cart]:

        return self.carts_repository.get_carts_by_user(
            user_id
        )

    def add_product(
        self,
        cart_id: int,
        product_id: int,
        quantity: int,
        user_id: int
    ) -> Cart:

        cart = self.get_cart(
            cart_id,
            user_id
        )

        self._validate_active_cart(cart)
        self._validate_quantity(quantity)
        self._validate_product_id(product_id)

        product = self.products_repository.get_by_id(
            product_id
        )

        if product is None:
            raise LookupError("Product not found.")

        if not product.is_active:
            raise ValueError(
                "Product is not available."
            )

        if quantity > product.stock:
            raise ValueError(
                "Insufficient product stock."
            )

        cart_product = (
            self.carts_repository.get_cart_product(
                cart_id,
                product_id
            )
        )

        try:
            if cart_product:

                new_quantity = (
                    cart_product.quantity
                    + quantity
                )

                if new_quantity > product.stock:
                    raise ValueError(
                        "Insufficient product stock."
                    )

                cart_product.quantity = new_quantity

            else:
                cart_product = CartProduct(
                    cart_id=cart.id,
                    product_id=product.id,
                    quantity=quantity,
                    price_at_added=Decimal(
                        str(product.price)
                    )
                )

                self.carts_repository.add_cart_product(
                    cart_product
                )

            self.session.commit()

            return (
                self.carts_repository
                .get_cart_with_products(cart.id)
            )

        except Exception:
            self.session.rollback()
            raise

    def update_product_quantity(
        self,
        cart_id: int,
        product_id: int,
        quantity: int,
        user_id: int
    ) -> Cart:

        cart = self.get_cart(
            cart_id,
            user_id
        )

        self._validate_active_cart(cart)
        self._validate_quantity(quantity)

        product = self.products_repository.get_by_id(
            product_id
        )

        if product is None:
            raise LookupError("Product not found.")

        if not product.is_active:
            raise ValueError(
                "Product is not available."
            )

        if quantity > product.stock:
            raise ValueError(
                "Insufficient product stock."
            )

        cart_product = (
            self.carts_repository.get_cart_product(
                cart_id,
                product_id
            )
        )

        if cart_product is None:
            raise LookupError(
                "Product is not in the cart."
            )

        try:
            cart_product.quantity = quantity

            self.session.flush()
            self.session.commit()

            return (
                self.carts_repository
                .get_cart_with_products(cart.id)
            )

        except Exception:
            self.session.rollback()
            raise

    def remove_product(
        self,
        cart_id: int,
        product_id: int,
        user_id: int
    ) -> Cart:

        cart = self.get_cart(
            cart_id,
            user_id
        )

        self._validate_active_cart(cart)
        self._validate_product_id(product_id)

        cart_product = (
            self.carts_repository.get_cart_product(
                cart_id,
                product_id
            )
        )

        if cart_product is None:
            raise LookupError(
                "Product is not in the cart."
            )

        try:
            self.carts_repository.delete_cart_product(
                cart_product
            )

            self.session.commit()

            return (
                self.carts_repository
                .get_cart_with_products(cart.id)
            )

        except Exception:
            self.session.rollback()
            raise

    def abandon_cart(
        self,
        cart_id: int,
        user_id: int
    ) -> Cart:

        cart = self.get_cart(
            cart_id,
            user_id
        )

        self._validate_active_cart(cart)

        try:
            cart.status = "ABANDONED"

            self.carts_repository.update(cart)

            self.session.commit()

            return cart

        except Exception:
            self.session.rollback()
            raise

    @staticmethod
    def _validate_active_cart(
        cart: Cart
    ) -> None:

        if cart.status != "ACTIVE":
            raise ValueError(
                "Only active carts can be modified."
            )

    @staticmethod
    def _validate_quantity(
        quantity: int
    ) -> None:

        if (
            isinstance(quantity, bool)
            or not isinstance(quantity, int)
        ):
            raise ValueError(
                "Quantity must be an integer."
            )

        if quantity <= 0:
            raise ValueError(
                "Quantity must be greater than zero."
            )

    @staticmethod
    def _validate_product_id(product_id):

        if (
            not isinstance(product_id, int)
            or isinstance(product_id, bool)
            or product_id <= 0
        ):
            raise ValueError(
                "product_id must be a positive integer."
            )